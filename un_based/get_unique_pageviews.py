import lib.db_connection as dbcon #@UnusedImport
import lib.google_api as gapi
from lib.functions import * #@UnusedWildImport
from _mysql_exceptions import IntegrityError
from apiclient.http import BatchHttpRequest
import time

START_DATE = '2014-04-01'
END_DATE = '2015-04-01'

def update_unique_pageviews_not_x_row(db, cur, page_id, unique_pageviews_not_x, start_date, end_date):
    try:
        cur.execute("""UPDATE ga_uniquepageviews SET uniquepageviews_not_x = """+str(unique_pageviews_not_x)+"""
            WHERE start_date='"""+START_DATE+"' AND end_date='"+END_DATE+"' AND page_id="+str(page_id))
        db.commit()
        return True
    except IntegrityError:
        print 'SKIPPED: Duplicate entry for ', page_id, start_date, end_date
        return False
      
def insert_unique_pageviews_row(db, cur, page_id, unique_pageviews, start_date, end_date):
    try:
        cur.execute("""INSERT INTO ga_uniquepageviews (page_id, uniquepageviews_x, start_date, end_date, timestamp) 
            VALUES ("""+str(page_id)+","+str(unique_pageviews)+",'"+start_date+"','"+end_date+"',NOW())")
        db.commit()
        return True
    except IntegrityError:
        print 'SKIPPED: Duplicate entry for ', page_id, start_date, end_date
        return False
                  
def insert_unique_pageviews(db, cur, rows, whitelist, start_date, end_date):
    count = 0
    for i in range(0, len(rows)):
        page_title = rows[i][0].encode('utf-8', 'replace')
        page_title = page_title[11:]
        if page_title in whitelist:
            unique_pageviews = rows[i][1] 
            page_id = get_page_id(cur, page_title)
            if insert_unique_pageviews_row(db, cur, page_id, unique_pageviews, start_date, end_date):
                print 'INSERTED:', page_id, page_title, unique_pageviews 
                count += 1
    return count

def process_response(request_id=None, response=None, exception=None):
    if exception:
        print 'ERROR ', exception
        # If exception = <HttpError 503 etc. (temporary error), try again later?
    else:
        if response is not None:
            rows = response['rows']
            if 'rows' in response:
                query_segment = response['query']['segment']
                page_title = de_escape_string(query_segment[query_segment.find('/index.php/')+11:])
                page_id = get_page_id(cur, page_title)
                unique_pageviews = rows[0][0]
                #print page_title, '\t|\t', page_id,  unique_pageviews
                if page_id != False:
                    if contains_x:
                        if insert_unique_pageviews_row(dbcon.db, cur, page_id, unique_pageviews, START_DATE, END_DATE):
                            print 'INSERTED:', page_id, page_title, unique_pageviews 
                    else:
                        if update_unique_pageviews_not_x_row(dbcon.db, cur, page_id, unique_pageviews, START_DATE, END_DATE):
                            print 'UPDATED:', page_id, page_title, unique_pageviews 
                else:
                    print 'ERROR: page_id not found for ', page_title
            else:
                print 'ERROR: no rows'
        else:
            print 'ERROR: No response'   

def get_unique_pageviews(db, cur, service, profile_id, whitelist, contains_article = True):
    batch = BatchHttpRequest()
    count = 1
    for page_title in whitelist:
        ids = "ga:" + profile_id
        metrics = "ga:uniquePageviews"
        dimensions = ""
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

print 'Getting navigation data for', len(whitelist), ' articles...'
service = gapi.initialize_service()
print 'Google API service initialized'

contains_x = True #compute X
get_unique_pageviews(dbcon.db, cur, service, gapi.PROFILE_ID, whitelist, contains_x)

contains_x = False #compute !X
get_unique_pageviews(dbcon.db, cur, service, gapi.PROFILE_ID, whitelist, contains_x)
