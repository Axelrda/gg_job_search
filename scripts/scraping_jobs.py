## IMPORT NECESSARY LIBRARIES
import pandas as pd
import csv 

# Scraping google jobs w/ serpapi
from serpapi import GoogleSearch

import json
import datetime

# generate UULE code from adress
import uule_grabber

# connect to SQLite database
import sqlite3

import os

BASE_DIR = '/home/axel/Documents/gg_job_search'
db_path = os.path.join(BASE_DIR, 'db/jobs_database.db')


API_KEY = '4b799b64af09be918f6d66d6e908184cba836c46596e58bfa8bf1fb9280e7f09' 
SEARCH_QUERIES = ["machine learning engineer", "data scientist", "data analyst", "data engineer"]
COUNTRY_CODE = 'FR'
TARGET_TYPE = 'Country'

def get_canonical_name():

    # Connect to SQLite and create a new database (or open it if it already exists)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # get canonical name for location of interest ==> FRANCE
    cursor.execute("""

        SELECT "Canonical Name" 
        FROM google_geotargets 
        WHERE "Target Type" = ? AND "Country Code" = ?;

    """, (TARGET_TYPE, COUNTRY_CODE))

    canonical_name = cursor.fetchall()[0][0]

    conn.close()

    return canonical_name

def collect_data_w_serpapi(uule_code):
    # Defining our search query + necessary parameters for GoogleSearch object

    # initialize jobs_all outside of the loop
    jobs_all = pd.DataFrame()

    # initialize all_jobs_queries outside of function
    all_jobs_queries = pd.DataFrame()

    #for date in datelist:
    for query in SEARCH_QUERIES:

        # serpapi will iterate up to n number of iterations
        for num  in range(50):

            start = num * 10

        # define parameters
            params = {
                'api_key': API_KEY,                              
                'device':'desktop',
                'uule': uule_code,                         # encoded location 
                'q': query,                          # search query
                'google_domain': 'google.fr',              
                'hl': 'fr',                                 # language of the search
                'gl': 'fr',                                 # country of the search
                'engine': 'google_jobs',                    # SerpApi search engine
                'start': start,                             # pagination
                'chips': 'date_posted:today'  #'data_range:2023-05-18'   #'date_posted:today'                 
            }

            # get results 
            search = GoogleSearch(params)
            results = search.get_dict()  # JSON file to python dict 

            # check if last search page, exceptions handling   
            try:
                if results['error'] == "Google hasn't returned any results for this query.":
                        break
            except KeyError:
                    print(f"Getting SerpAPI data for page: {start} of '{query}' results")
            else:
                    continue

            # create dataframe of 10 pulled results
            jobs = results['jobs_results']
            jobs = pd.DataFrame(jobs)
            jobs = pd.concat([pd.DataFrame(jobs), 
                            pd.json_normalize(jobs['detected_extensions'])], #convert detected extension key in json files into pandas df
                            axis=1).drop('detected_extensions', axis=1) # drop json object
            jobs['date_time'] = datetime.datetime.now() # add extraction date column for job results

            # concat dataframe of 10 pulled results with jobs_all
            if start == 0:
                    jobs_all = jobs
            else:
                    jobs_all = pd.concat([jobs_all, jobs])

            # assign ongoing query to pulled results dataframe
            jobs_all['search_query'] = query

            # concat dataframe of all pulled results with all_jobs_queries 
            all_jobs_queries = pd.concat([all_jobs_queries, jobs_all])

    # get rid of duplicates before export
    all_jobs_queries.drop_duplicates(subset='description', inplace=True)

    # reindex columns to match the order of existing data
    all_jobs_queries = all_jobs_queries.reindex(columns=['title', 'company_name', 'location', 'via', 'description',
       'job_highlights', 'related_links', 'thumbnail', 'extensions', 'job_id',
       'posted_at', 'schedule_type', 'date_time', 'search_query'])
    
    all_jobs_queries.to_csv('all_jobs.csv', index=False)

    # convert value to str format (sql database doesn't accept list type)
    for column in all_jobs_queries.columns:
        all_jobs_queries[column] = all_jobs_queries[column].apply(lambda x: str(x) if isinstance(x, list) else x)

    # export data to database
    with sqlite3.connect(db_path) as conn:
        all_jobs_queries.to_sql('unprocessed_data', conn, if_exists='append', index=False)

    print("Shape of df:", all_jobs_queries.shape)


if __name__ == "__main__":

    canonical_name = get_canonical_name()

    # convert canonical_name to uule code
    uule_code = uule_grabber.uule(canonical_name)

    collect_data_w_serpapi(uule_code)


