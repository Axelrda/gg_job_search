import os

API_KEY = os.environ.get("API_KEY")
SEARCH_QUERIES = os.environ.get("SEARCH_QUERIES").strip(",")
COUNTRY_CODE = os.environ.get("COUNTRY_CODE")
TARGET_TYPE = os.environ.get("TARGET_TYPE")
DB_PATH = os.environ.get("DB_PATH")
