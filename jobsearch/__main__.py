import argparse
from jobsearch.source.serpapi import scrape_google_search_jobs_with_serpapi
from jobsearch.utils import convert_dict_columns_to_json
from jobsearch.database import export_dataframe_to_postgresql
from jobsearch.ml_logic.lang_classifier import detect_language
from jobsearch.params import *

if __name__ == "__main__":

    # Create the parser and add arguments
    parser = argparse.ArgumentParser(description='Scrape jobs using SerpAPI.')
    parser.add_argument('-d', '--date', type=str, default='today', help='Date to scrape jobs for (default: today). Type str')
    parser.add_argument('-n', '--number', type=int, default=50, help='Number of google job search pages to scrape for (default: 50). Useful to test without wasting serpapi credits. Type int.')
    parser.add_argument('-c', '--cloud', action="store_true", help="Export scraped data to cloud. If not set, defaults to local storage.")

    # Parse the arguments
    args = parser.parse_args()

    # scraping jobs
    new_jobs = scrape_google_search_jobs_with_serpapi(SERPAPI_SEARCH_QUERIES, SERPAPI_KEY, FRANCE_UULE_CODE, args.date, args.number)

    # prep data for postgresql storage
    new_jobs = convert_dict_columns_to_json(new_jobs, ['related_links', 'job_highlights'])
    
    # exporting to google cloud sql database
    export_dataframe_to_postgresql(new_jobs, export_to_cloud=args.cloud)
    
    # Detect language for each record
    
    # new_jobs['language'] = detect_language(model_path='../models/xlm-roberta-base-language-detection/', new_jobs.description.tolist())

    # Filter for French records
    # french_jobs = new_jobs[new_jobs['language'] == 'fr']

    # Export French records to the new table
    # export_dataframe_to_postgresql(french_jobs, table_name='french_jobs', export_to_cloud=bool(args.cloud))
