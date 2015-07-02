from lib.functions import * #@UnusedWildImport
#create whitelist, pages you want to generate recommendations for
#makes the other processes much faster
import create_whitelist #you can comment this if you have already created a whitelist

#get unique pageviews
import get_unique_pageviews

#get path pair matrix
import get_path_pair_matrix

START_DATE = '2014-04-01'
END_DATE = '2015-04-01'

cur = dbcon.db.cursor()
whitelist_page_ids = get_whitelist_page_ids(cur)

count = 0
for page_id in whitelist_page_ids:
    cur.execute("""SELECT uniquepageviews_x, uniquepageviews_not_x
                FROM `ga_uniquepageviews` 
                WHERE start_date = '""" + START_DATE + """' AND end_date = '""" + END_DATE + """'
                AND page_id =""" + str(page_id))
    result = cur.fetchall()
    for row in result:
        pageviews_x = row[0]
        pageviews_not_x = row[1]

    unscores = {}
    cur.execute("""SELECT PX.page_title AS titleX, PY.page_title AS titleY, PY.page_id AS page_id_Y, PP.uniquepageviews_x, PP.uniquepageviews_not_x, PV.uniquepageviews_x AS y,
                CASE WHEN EXISTS (SELECT * FROM ec_wikipagelinks WHERE pl_from = """+str(page_id)+""" AND pl_title = PY.page_title) THEN 'Link in article' ELSE 'None' END AS link
                FROM `ga_pathpairmatrix` PP
                JOIN ec_wikipage PX ON PX.page_id = PP.page_id_X
                JOIN ec_wikipage PY ON PY.page_id = PP.page_id_Y
                JOIN ga_uniquepageviews PV ON PV.page_id = PY.page_id AND PV.start_date = '""" + START_DATE + """' AND PV.end_date = '""" + END_DATE + """'
                WHERE PP.page_id_X = """ + str(page_id))
    result = cur.fetchall()
    for row in result:
        page_id_Y = row[2]
        x_y = row[3]
        y = row[5]
        not_x_y = y - x_y
        
        #compute formula
        if(pageviews_x != 0):
            x_y_over_x = x_y / pageviews_x
        else:
            x_y_over_x = 0
        
        if(pageviews_not_x != 0):
            not_x_y_over_not_x = not_x_y / pageviews_not_x
        else:
            not_x_y_over_not_x = 0
        
        if(not_x_y_over_not_x != 0):
            score = round(x_y_over_x / not_x_y_over_not_x,4)
        else:
            score = 0
            
        unscores[page_id_Y] = score
    if(unscores):
        maxvaluekey = max(unscores.iterkeys(), key=(lambda key: unscores[key]))
        maxvalue = unscores[maxvaluekey]
    
        for page_id_Y, score in unscores.iteritems():
            if(maxvalue != 0):
                unscores[page_id_Y] = score / maxvalue
            else:
                unscores[page_id_Y] = 0
                
            cur.execute("""INSERT INTO demo_recommendations (page_id_X, page_id_Y, score, algorithm, timestamp) 
                VALUES ("""+str(page_id)+""","""+str(page_id_Y)+""","""+str(score)+""","""+"""'user-navigation-based', NOW())""")
            dbcon.commit()
    count += 1
            
print count + ' recommendations inserted!'