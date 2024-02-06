import argparse

from jobsearch.source.serpapi import scrape_google_search_jobs_with_serpapi
from jobsearch.utils import convert_dict_columns_to_json, convert_json_columns_to_dict
from jobsearch.database import export_dataframe_to_postgres
from jobsearch.params import *

if __name__ == "__main__":

    # Create the parser and add arguments
    parser = argparse.ArgumentParser(description='Scrape jobs using SerpAPI.')
    parser.add_argument('-d', '--date', type=str, default='today', help='Date to scrape jobs for (default: today). Type str')
    parser.add_argument('-n', '--number', type=int, default=50, help='Number of google job search pages to scrape for (default: 50). Useful to test without wasting serpapi credits. Type int.')

    # Parse the arguments
    args = parser.parse_args()

    # scraping jobs
    all_jobs = scrape_google_search_jobs_with_serpapi(SERPAPI_SEARCH_QUERIES, SERPAPI_KEY, FRANCE_UULE_CODE, args.date, args.number)

    # prep data for postgresql storage
    all_jobs = convert_dict_columns_to_json(all_jobs, ['related_links', 'job_highlights'])

    # exporting to google cloud sql database
    export_dataframe_to_postgres(all_jobs)
