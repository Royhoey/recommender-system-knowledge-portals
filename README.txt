== About ==

The Python code in this repository can be used to generate recommendations
for knowledge portals that are built with MediaWiki and have a Google Analytics
account. Some knowledge about Python and MySQL is needed to modify this code
to work with your site.

== Instructions ==

Create a demo_recommendations table in your MediaWiki database to store the recommendations in.
You can import demo_recommendations.sql to do this.

Setup your database connection in lib/db_connection.py
Setup your google analytics account in lib/google_api.py 
(https://developers.google.com/api-client-library/python/apis/analytics/v2.4) 

Execute the files in the following order:
1. un_based/un_based_algorithm.py
2. content_based/content_based.py
3. hybrid/hybrid.py

