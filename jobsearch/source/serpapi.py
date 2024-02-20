import pandas as pd

import sqlite3
import argparse
import datetime

import serpapi
from sqlalchemy import create_engine

from jobsearch.params import *


def scrape_google_search_jobs_with_serpapi(SERPAPI_SEARCH_QUERIES, SERPAPI_KEY, uule_code, date="today", page_num=50):

    all_jobs = pd.DataFrame()

    print("Starting jobs scraping ...")

    for query in SERPAPI_SEARCH_QUERIES:

        for num  in range(page_num):

            start_page = num * 10

        # define parameters
            params = {
                'api_key': SERPAPI_KEY,
                'device':'desktop',
                'uule': uule_code,                         # encoded location
                'q': query,                          # search query
                'google_domain': 'google.fr',
                'hl': 'fr',                                 # language of the search
                'gl': 'fr',                                 # country of the search
                'engine': 'google_jobs',                    # SerpApi search engine
                'start': start_page,                             # pagination
                'chips': f'date_posted:{date}'  #'date_range:2023-05-18'   #'date_posted:today'
            }

            # query serapi
            search = serpapi.search(params=params)
            # get results as dict
            res = search.as_dict()

            # check if last search page, exceptions handling
            try:
                if res['error'] == "Google hasn't returned any results for this query.":
                    break
            except KeyError:
                print(f"Getting SerpAPI data for results: {start_page} - {start_page+10} of '{query}' query")
            else:
                continue

            # discard search metadata, keep job results
            jobs = res['jobs_results']

            # convert to dataframe
            jobs_df = pd.DataFrame(jobs)
            # convert json columns to dataframe
            normalized_extensions = pd.json_normalize(jobs_df['detected_extensions'])

            ten_jobs_df = pd.concat([jobs_df, normalized_extensions],axis=1)
            ten_jobs_df = ten_jobs_df.drop('detected_extensions', axis=1)
            ten_jobs_df['date_time'] = datetime.datetime.now()
            ten_jobs_df['search_query'] = query
            ten_jobs_df['local_sync_timestamp'] = pd.NaT

            # concat dataframe of 10 pulled results with all_jobs
            all_jobs = pd.concat([all_jobs, ten_jobs_df])

    all_jobs = all_jobs.drop_duplicates(subset='description')

    all_jobs = all_jobs.reindex(columns=['title', 'company_name', 'location', 'via', 'description',
        'job_highlights', 'related_links', 'thumbnail', 'extensions', 'job_id',
        'posted_at', 'schedule_type', 'date_time', 'search_query'])

    all_jobs = all_jobs.reset_index(drop=True)

    print("✅ Scraping jobs finished")

    print(f"{all_jobs.shape[0]} jobs were scraped")

    return all_jobs
