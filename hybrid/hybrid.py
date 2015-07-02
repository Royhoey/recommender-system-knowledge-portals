import lib.db_connection as dbcon #@UnusedImport
from lib.functions import * #@UnusedWildImport

cur = dbcon.db.cur()

whitelist_page_ids = get_whitelist_page_ids(cur)

count = 0
for page_id in whitelist_page_ids:
    un_based_recommendations = get_recommendations(cur, page_id, 'user-navigation-based')
    unscores = {}
    for row in un_based_recommendations:
        page_id_Y = row[0]
        score = row[1]
        unscores[page_id_Y] = score
    
    content_based_recommendations = get_recommendations(cur, page_id, 'content-based')
    for row in content_based_recommendations:
        page_id_Y = row[0]
        score = row[1]
        if page_id_Y in unscores:
            score = (score + unscores[page_id_Y]) / 2 #adjust content sim score with popularity score
        
        #insert recommendations
        cur.execute("""INSERT INTO demo_recommendations (page_id_X, page_id_Y, score, algorithm, timestamp) 
                VALUES ("""+str(page_id)+""","""+str(page_id_Y)+""","""+str(score)+""","""+"""'hybrid', NOW())""")
        dbcon.commit()
    count += 1
    
print count + ' hybrid recommendations inserted!' 

        