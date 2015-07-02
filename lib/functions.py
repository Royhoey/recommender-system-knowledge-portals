import lib.db_connection as dbcon

def get_recommendations(cur, page_id, algorithm):
    cur.execute("""SELECT PY.page_id AS page_id_Y, REC.score,
            CASE WHEN EXISTS 
                (SELECT * FROM ec_wikipagelinks WHERE pl_from = """+str(page_id)+""" AND pl_title = PY.page_title) 
                THEN 'Link in article' ELSE 'None' END AS link
            FROM `demo_recommendations` REC
            JOIN ec_wikipage PX ON PX.page_id = REC.page_id_X
            JOIN ec_wikipage PY ON PY.page_id = REC.page_id_Y
            WHERE algorithm = '"""+algorithm+"""' AND REC.page_id_X =""" + str(page_id))
    result = cur.fetchall()
    return result

def get_page_id(cur, page_title):
    try:
        page_title = dbcon.MySQLdb.escape_string(page_title)
        cur.execute("SELECT page_id FROM ec_wikipage WHERE page_namespace = 0 AND page_title = '" + str(page_title) + "'")
        if(cur.rowcount > 0):
            row = cur.fetchone()
            return row[0]
        else:
            return False
    except UnicodeEncodeError:
        return False
    
def get_page_title(cur, page_id, url = False):
    cur.execute("SELECT page_title FROM ec_wikipage WHERE page_id= '" + str(page_id) + "'")
    if(cur.rowcount > 0):
        row = cur.fetchone()
        if(url):
            return '/index.php/' + row[0]
        else:
            return row[0]
    else:
        return False
    
def title_to_url(page_title):
    return '/index.php/' + page_title

def escape_string(page_title):
    return page_title.replace(',', '\,')

def de_escape_string(page_title):
    return page_title.replace('\,', ',')


def get_whitelist_page_ids(cur):
    whitelist = []
    cur.execute("""SELECT page_id
    FROM `ec_whitelist`""")
    result = cur.fetchall()
    for row in result:
        page_id = row[0]
        whitelist.append(page_id)
    return whitelist

def get_whitelist_page_titles(cur):
    whitelist = []
    cur.execute("""SELECT page_title
        FROM `ec_whitelist`""")
    result = cur.fetchall()
    for row in result:
        page_title = row[0]
        whitelist.append(page_title)
    return whitelist

def process_text(text):
    text = text.replace("'''", "")
    text = text[text.find("}}") + 2:] #remove until end of infobox
    text = text[:text.find("== Further Reading ==")] #cut further reading part
    return text

def get_text(cur, page_id, decoded = True):
    cur.execute("""SELECT CONVERT(old_text USING utf8mb4) AS text
    FROM `ec_whitelist_content` WHERE page_id = """ + str(page_id))
    row = cur.fetchone()
    if(decoded):
        return process_text(row[0].decode('utf8', 'replace'))
    else:
        return process_text(row[0])

def get_whitelist_content_text(cur):
    whitelist = []
    cur.execute("""SELECT CONVERT(old_text USING utf8mb4) AS text
    FROM `ec_whitelist_content`""")
    result = cur.fetchall()
    for row in result:
        text = process_text(row[0].decode('utf8', 'replace'))
        whitelist.append(text)
    print 'Whitelist retrieved!'
    return whitelist

def get_whitelist_content_page_ids(cur):
    whitelist = []
    cur.execute("""SELECT page_id
    FROM `ec_whitelist_content`""")
    result = cur.fetchall()
    for row in result:
        whitelist.append(row[0])
    print 'Whitelist retrieved!'
    return whitelist

