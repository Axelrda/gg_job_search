import sqlite3
import argparse
import datetime
import pandas as pd

# Scraping google jobs w/ serpapi
import serpapi

# generate UULE code from adress
import uule_grabber


from jobsearch.params import *


def get_canonical_name(DB_PATH, GOOGLE_GEOTARGET_TARGET_TYPE, GOOGLE_GEOTARGET_COUNTRY_CODE):

    # Connect to SQLite and create a new database (or open it if it already exists)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # get canonical name for location of interest ==> FRANCE
        cursor.execute("""
            SELECT "Canonical Name"
            FROM google_geotargets
            WHERE "Target Type" = ? AND "Country Code" = ?;
        """, (GOOGLE_GEOTARGET_TARGET_TYPE, GOOGLE_GEOTARGET_COUNTRY_CODE))

        canonical_name = cursor.fetchall()[0][0]

    finally:
        conn.close()

    return canonical_name

def convert_to_uule(canonical_name):

    # convert canonical_name to uule code
    uule_code = uule_grabber.uule(canonical_name)

    return uule_code

def scrape_jobs_serpapi(SERPAPI_SEARCH_QUERIES, SERPAPI_KEY, uule_code, date="today"):

    all_jobs = pd.DataFrame()

    print("Starting jobs scraping ...")

    for query in SERPAPI_SEARCH_QUERIES:

        for num  in range(50):

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
                print(f"Getting SerpAPI data for page: {start_page} - {start_page+10} of '{query}' results")
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

            # concat dataframe of 10 pulled results with all_jobs
            all_jobs = pd.concat([all_jobs, ten_jobs_df])

    all_jobs = all_jobs.drop_duplicates(subset='description')

    all_jobs = all_jobs.reindex(columns=['title', 'company_name', 'location', 'via', 'description',
        'job_highlights', 'related_links', 'thumbnail', 'extensions', 'job_id',
        'posted_at', 'schedule_type', 'date_time', 'search_query'])

    all_jobs = all_jobs.reset_index(drop=True)

    print("Scraping jobs finished ✅")

    print(f"{all_jobs.shape[0]} jobs were scraped")

    return all_jobs


def export_to_sqlite(DB_PATH, all_jobs):
    #### EXPORT TO SQLITE DATABASE ####
    # convert value to str format (sql database doesn't accept list type)
    for column in all_jobs.columns:
        all_jobs[column] = all_jobs[column].apply(lambda x: str(x) if isinstance(x, list) else x)

    print("Now, exporting data to SQL database ...")

    # export data to database
    with sqlite3.connect(DB_PATH) as conn:
        all_jobs.to_sql('unprocessed_data', conn, if_exists='append', index=False)

    print("Data exported ✅")


if __name__ == "__main__":
    # Create the parser and add arguments
    parser = argparse.ArgumentParser(description='Scrape jobs using SerpAPI.')
    parser.add_argument('-d', '--date', default='today', help='Date to scrape jobs for (default: today). Format YYYY-MM-DD.')

    # Parse the arguments
    args = parser.parse_args()

    # Use the date argument
    all_jobs = scrape_jobs_serpapi(SERPAPI_SEARCH_QUERIES, SERPAPI_KEY, FRANCE_UULE_CODE, args.date)
    export_to_sqlite(DB_PATH, all_jobs)
