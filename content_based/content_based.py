import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity #takes length of text into account
from sklearn.metrics.pairwise import euclidean_distances #compares distance between vectors
import lib.db_connection as dbcon #@UnusedImport
import lib.google_api as gapi
from lib.functions import * #@UnusedWildImport
from _mysql_exceptions import IntegrityError
import operator
import sys

VERSION = 'v2' #change to v1 for CountVectorizer, v2 for TfidfVectorizer

# initialize connection
cur = dbcon.db.cursor()

def get_page_title(cur, whitelist_id):
    cur.execute("SELECT page_title FROM ec_whitelist_content WHERE whitelist_id = " + str(whitelist_id))
    if(cur.rowcount > 0):
        row = cur.fetchone()
        return row[0]
    else:
        return False

def get_page_id_from_whitelist(cur, whitelist_id):
    cur.execute("SELECT page_id FROM ec_whitelist_content WHERE whitelist_id = " + str(whitelist_id))
    if(cur.rowcount > 0):
        row = cur.fetchone()
        return row[0]
    else:
        return False

def get_page_id(cur, page_title):
    page_title = dbcon.escape_string(page_title)
    cur.execute("SELECT page_id FROM ec_wikipage WHERE page_namespace = 0 AND page_title = '" + str(page_title) + "'")
    if(cur.rowcount > 0):
        row = cur.fetchone()
        return row[0]
    else:
        return -1

def get_whitelist_id_from_page_id(cur, page_id):
    cur.execute("SELECT whitelist_id FROM ec_whitelist_content WHERE page_id = '" + str(page_id) + "'")
    if(cur.rowcount > 0):
        row = cur.fetchone()
        return row[0]
    else:
        return -1

def get_whitelist_id(cur, page_title):
    page_title = dbcon.escape_string(page_title)
    cur.execute("SELECT whitelist_id FROM ec_whitelist_content WHERE page_title = '" + str(page_title) + "'")
    if(cur.rowcount > 0):
        row = cur.fetchone()
        return row[0]
    else:
        return -1
    
def process_text(text):
    text = text.replace("'''", "")
    text = text[text.find("}}") + 2:] #remove until end of infobox
    text = text[:text.find("== Further Reading ==")] #cut further reading part
    return text

def get_whitelist_page_ids(cur):
    whitelist = []
    cur.execute("""SELECT page_id
    FROM `ec_whitelist_content`""")
    result = cur.fetchall()
    for row in result:
        whitelist.append(row[0])
    print 'Whitelist retrieved!'
    return whitelist

def get_whitelist(cur):
    whitelist = []
    cur.execute("""SELECT CONVERT(old_text USING utf8mb4) AS text
    FROM `ec_whitelist_content`""")
    result = cur.fetchall()
    for row in result:
        text = process_text(row[0].decode('utf8', 'replace'))
        whitelist.append(text)
    print 'Whitelist retrieved!'
    return whitelist

def get_text(cur, page_id):
    cur.execute("""SELECT CONVERT(old_text USING utf8mb4) AS text
    FROM `ec_whitelist_content` WHERE page_id = """ + str(page_id))
    row = cur.fetchone()
    return process_text(row[0].decode('utf8', 'replace'))

def insert_content_based_recommendation(db, cur, page_id_X, page_id_Y, score, version):
    try:
        cur.execute("""INSERT INTO demo_recommendations (page_id_X, page_id_Y, score, algorithm, timestamp) 
            VALUES ("""+str(page_id_X)+","+str(page_id_Y)+","+str(score)+",'content-based-"+version+"',NOW())")
        db.commit()
        print 'INSERTED: ', page_id_X, page_id_Y, 'content-based-'
        return True
    except IntegrityError:
        print 'SKIPPED: Duplicate entry for ', page_id_X, page_id_Y, 'content-based-'
        return False
    

def print_ranking(db, cur, page_id_X, ranked_scores):
    count = 0
    for i in reversed(xrange(0,len(ranked_scores))):
        if(count < 30):
            whitelist_id = ranked_scores[i][0]
            score = ranked_scores[i][1]
            if(score != 1.0):
                page_id_Y = get_page_id_from_whitelist(cur, whitelist_id)
                print i, ' | ', page_id_Y, ' | ', get_page_title(cur, whitelist_id), ' | ', score
                insert_content_based_recommendation(db, cur, page_id_X, page_id_Y, score, VERSION)
                count += 1
        
def get_ranked_scores(cur, similarities):
    key_value_dict = {}
    index = 1 #whitelist id in tabel begint op 1 ipv 0
    for score in similarities:
        key_value_dict[index] = score
        index += 1 
    #sort values
    ranked_scores = sorted(key_value_dict.items(), key=operator.itemgetter(1))
    return ranked_scores
        
def get_row_similarities(dist, row):
    similarities = []
    columns = dist.shape[1]
    for i in range(0,columns):
        sim = round(dist[row,i],2)
        similarities.append(sim)
    return similarities

def print_word_frequencies(vocab, doc_index):
    for word in vocab:
        index = list(vocab).index(word)
        print index, word, dtm[doc_index, index]

def get_word_frequency(dtm, doc_index, word):
    return dtm[doc_index, vocab==word]

#Create test dictionary with three articles
dictionary = []
whitelist = get_whitelist(cur)
count = 1

for text in whitelist:
    dictionary.append(text)
      
print 'Dictionary created!'

if(VERSION == 'v2'):
    vectorizer = TfidfVectorizer(stop_words='english', strip_accents='unicode')
elif (VERSION == 'v1'):
    vectorizer = CountVectorizer(stop_words='english', strip_accents='unicode')
    
dtm = vectorizer.fit_transform(dictionary) #document term matrix from dictionary
vocab = vectorizer.get_feature_names()

dtm = dtm.toarray() #convert matrix to array
vocab = np.array(vocab)

print 'Cosine sim distance matrix:'
dist = cosine_similarity(dtm) #this measures similarity. If you want to measure distance, use 1 - cosine_similarity(dtm)
print np.round(dist,2)

whitelist_page_ids = get_whitelist_page_ids(cur)

for page_id_X in whitelist_page_ids:
    whitelist_id = get_whitelist_id_from_page_id(cur, page_id_X)
    similarities = get_row_similarities(dist,whitelist_id-1)
    ranked_scores = get_ranked_scores(cur, similarities)
    print_ranking(dbcon, cur, page_id_X, ranked_scores)

print 'All done!'
#close the connection
cur.close()
dbcon.close()
