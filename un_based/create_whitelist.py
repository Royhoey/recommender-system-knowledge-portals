import lib.db_connection as dbcon #@UnusedImport

cur = dbcon.db.cursor()

#create whitelist table
cur.execute(""" CREATE TABLE IF NOT EXISTS `ec_whitelist2` (
  `whitelist_id` int(11) NOT NULL AUTO_INCREMENT,
  `page_id` int(8) unsigned NOT NULL,
  `page_title` varchar(255) CHARACTER SET latin1 COLLATE latin1_bin NOT NULL,
  `old_text` mediumblob NOT NULL,
  PRIMARY KEY (`whitelist_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ; """)
print 'Whitelist table created!'
#fill whitelist table

#modify this query so that it includes your own filters
cur.execute(""" INSERT INTO `ec_whitelist2` (page_id, page_title, old_text) 
(
SELECT page_id,  page_title, CONVERT(T.old_text USING utf8mb4) AS text
FROM `ec_wikipage` P
JOIN ec_wikirevision R ON P.page_id = R.rev_page
JOIN ec_wikitext T ON R.rev_text_id = T.old_id
WHERE page_namespace = 0
AND page_title NOT LIKE "%(Nano)%"
AND rev_text_id = 
(SELECT MAX(rev_text_id)
FROM `ec_wikirevision` 
JOIN ec_wikitext T ON T.old_id = rev_text_id
WHERE rev_page = P.page_id AND CONVERT(T.old_text USING utf8mb4) LIKE '{{Infobox%')
AND rev_timestamp =
(SELECT MAX(rev_timestamp)
FROM `ec_wikirevision` 
JOIN ec_wikitext T ON T.old_id = rev_text_id
WHERE rev_page = P.page_id AND CONVERT(T.old_text USING utf8mb4) LIKE '{{Infobox%')
AND EXISTS (SELECT cl_to 
                FROM ec_wikicategorylinks 
                WHERE P.page_id = cl_from 
                AND (cl_to = 'Operational_Issues' OR cl_to = 'Human_Performance' OR cl_to = 'Accidents_and_Incidents' OR cl_to = 'Glossary'))

)""")
print 'Whitelist table filled!'