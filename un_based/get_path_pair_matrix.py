import lib.db_connection as dbcon #@UnusedImport
import lib.google_api as gapi
from lib.functions import * #@UnusedWildImport
from _mysql_exceptions import IntegrityError
from apiclient.http import BatchHttpRequest
import time

START_DATE = '2014-04-01' #INSERT A START DATE
END_DATE = '2015-04-01' #INSERT AN END DATE

def update_path_pair(page_id_X, page_id_Y, unique_pageviews):
    try:
        cur.execute("UPDATE ga_pathpairmatrix SET uniquepageviews_not_x="+str(unique_pageviews)+"""
             WHERE start_date='"""+START_DATE+"' AND end_date='"+END_DATE+"' AND page_id_X="+str(page_id_X)+" AND page_id_Y="+str(page_id_Y))
        dbcon.db.commit()
        return True
    except IntegrityError:
        print 'SKIPPED: Duplicate entry for ', page_id_X, page_id_Y, START_DATE, END_DATE
        return False

def insert_path_pair(page_id_X, page_id_Y, unique_pageviews):
    try:
        cur.execute("""INSERT INTO ga_pathpairmatrix (page_id_X, page_id_Y, uniquepageviews_x, start_date, end_date, timestamp) 
            VALUES ("""+str(page_id_X)+","+str(page_id_Y)+","+str(unique_pageviews)+",'"+START_DATE+"','"+END_DATE+"',NOW())")
        dbcon.db.commit()
        return True
    except IntegrityError:
        print 'SKIPPED: Duplicate entry for ', page_id_X, page_id_Y, START_DATE, END_DATE
        return False

def process_response(request_id=None, response=None, exception=None):
    if exception:
        print 'ERROR ', exception
        # If exception = <HttpError 503 etc. (temporary error), try again later?
    else:
        if response is not None:
            whitelist_page_ids = get_whitelist_page_ids(cur)
            if 'rows' in response:
                rows = response['rows']
                query_segment = response['query']['segment']
                page_title_X = de_escape_string(query_segment[query_segment.find('/index.php/')+11:])
                page_id_X = get_page_id(cur, page_title_X)
                if page_id_X != False:
                    path_pair_count = 0
                    for i in range(0, len(rows)): #get score for each path pair combination
                        page_title_Y = rows[i][0]
                        page_title_Y = page_title_Y[11:]
                        page_id_Y = get_page_id(cur,page_title_Y)
                        if page_id_Y != False:
                            unique_pageviews = rows[i][1]
                            if(page_id_X != page_id_Y):
                                if page_id_Y in whitelist_page_ids: 
                                    if contains_x:
                                        insert_path_pair(page_id_X,page_id_Y, unique_pageviews)
                                    else:
                                        update_path_pair(page_id_X,page_id_Y, unique_pageviews)
                                    path_pair_count += 1
                print 'Inserted/updated', path_pair_count, 'path pairs for', page_title_X   
            else:
                print 'ERROR: No rows'       
        else:
            print 'ERROR: No response'   

def get_path_pair_matrix(db, cur, service, profile_id, whitelist, contains_article = True):
    batch = BatchHttpRequest()
    count = 1
    for page_title in whitelist:
        ids = "ga:" + profile_id
        metrics = "ga:uniquePageviews"
        dimensions = "ga:pagePath"
        sort = "-ga:uniquePageviews"
        operator = "==" if contains_article else "!="
        segment = "sessions::condition::ga:pagePath"+operator+"/index.php/" + escape_string(page_title)
        batch.add(service.data().ga().get(
           ids=ids, 
           start_date=START_DATE, 
           end_date=END_DATE, 
           metrics=metrics, 
           dimensions=dimensions,
           segment=segment,
           sort=sort,fields='rows,query'), callback=process_response)
        if count % 10 == 0 or count == len(whitelist): #user rate limit is 10 requests per second
            print 'Executing batch HTTP request...'
            time.sleep(1) # 1 second between user requests
            batch.execute() 
            batch = BatchHttpRequest() #create new object
        count += 1
        
    print 'All done!'

cur = dbcon.db.cursor()
whitelist = get_whitelist_page_titles(cur)

print 'Getting path-pair matrix data for', len(whitelist), ' articles...'
service = gapi.initialize_service()
print 'Google API service initialized'

contains_x = True #compute X
get_path_pair_matrix(dbcon.db, cur, service, gapi.PROFILE_ID, whitelist, contains_x)

contains_x = False #compute !X
get_path_pair_matrix(dbcon.db, cur, service, gapi.PROFILE_ID, whitelist, contains_x)
