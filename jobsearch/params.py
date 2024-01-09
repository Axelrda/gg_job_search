import os

SERPAPI_KEY = os.environ.get("API_KEY")
SEARCH_QUERIES = os.environ.get("SEARCH_QUERIES").split(',')
COUNTRY_CODE = os.environ.get("COUNTRY_CODE")
TARGET_TYPE = os.environ.get("TARGET_TYPE")
DB_PATH = os.environ.get("DB_PATH")
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
