import pandas as pd
import sqlite3
import logging
from contextlib import suppress
import sqlalchemy
from sqlalchemy import create_engine
from jobsearch.params import *
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.types import Integer, Text


SCRAPE_JOBS_DTYPES = {
    'title': Text,
    'company_name': Text,
    'location': Text,
    'via': Text,
    'description': Text,
    #'job_highlights': JSONB,  
    #'related_links': JSONB,   
    'thumbnail': Text,
    'extensions': Text,
    'job_id': Text,
    'posted_at': Text,
    'schedule_type': Text,
    'date_time': TIMESTAMP,
    'search_query': Text,
    'local_sync_timestamp': TIMESTAMP
}


def get_canonical_name(db_path, google_geotarget_target_type, google_geotarget_country_code):

    # Connect to SQLite and create a new database (or open it if it already exists)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # get canonical name for location of interest ==> FRANCE
        cursor.execute("""
            SELECT "Canonical Name"
            FROM google_geotargets
            WHERE "Target Type" = ? AND "Country Code" = ?;
        """, (google_geotarget_target_type, google_geotarget_country_code))

        canonical_name = cursor.fetchall()[0][0]

    finally:
        conn.close()

    return canonical_name

def deduplicate_sqlite_data(db_path):
    conn = sqlite3.connect(db_path)
    print(db_path)
    c = conn.cursor()
    print("Opening Database ...")
    try:
        print("Starting data deduplication - first pass ...")
        # Start a transaction
        c.execute('BEGIN TRANSACTION;')

        c.execute('DROP TABLE IF EXISTS deduplicated_data;')

        c.execute('''
            CREATE TABLE raw_data AS
                SELECT title, company_name, location, via, description, job_highlights, related_links, thumbnail, extensions, job_id, posted_at, schedule_type, date_time, search_query
                FROM (
                    SELECT *,
                    ROW_NUMBER() OVER(PARTITION BY description) AS rn
                    FROM rawdata
                )
                WHERE rn = 1;
        ''')

        # Commit the transaction if no errors
        conn.commit()

    except sqlite3.Error as e:
        print("An error occurred:", e.args[0])
        # Rollback the transaction if there was an error
        conn.rollback()
    finally:
        print("Closing database ...")
        # Close the connection
        conn.close()

def fetch_data_from_local_sqlite(db_path, table='raw_data'):
    try:
        conn = sqlite3.connect(db_path, timeout=30)
        c = conn.cursor()
        c.execute(f"""SELECT * FROM {table}""")
        rows = c.fetchall()
        columns = [column[0] for column in c.description]
        data = pd.DataFrame(rows, columns=columns)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()
    return data

def export_to_sqlite(db_path, df):
    #### EXPORT TO SQLITE DATABASE ####
    # convert value to str format (sql database doesn't accept list type)
    for column in df.columns:
        df[column] = df[column].apply(lambda x: str(x) if isinstance(x, list) else x)

    print("Now, exporting data to SQL database ...")

    # export data to database
    with sqlite3.connect(db_path) as conn:
        df.to_sql('raw_data', conn, if_exists='append', index=False)

    print("Data exported ✅")

# Helper function to create the database path based on the cloud option
def create_db_path(export_to_cloud: bool) -> str:
    """Create the database path based on the cloud option.

    Args:
        export_to_cloud (bool): Whether to use the cloud or local database.

    Returns:
        str: The database path.
    """
    if export_to_cloud:
        print("Using CLOUD postgres database ...")
        db_path = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_GCS_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'
    else:
        print("Using LOCAL postgres database ...")
        db_path = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_LOCALHOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'
    return db_path

# Helper function to create the engine based on the database path
def create_db_engine(db_path: str) -> sqlalchemy.engine.Engine:
    """Create the engine based on the database path.

    Args:
        db_path (str): The database path.

    Returns:
        sqlalchemy.engine.Engine: The engine object.
    """
    engine = create_engine(db_path)
    return engine

# Helper function to handle the try-except logic for the database path and engine creation
def handle_db_error(func):
    """Handle the try-except logic for the database path and engine creation.

    Args:
        func (function): The function that needs the try-except logic.

    Returns:
        function: The wrapped function with the try-except logic.
    """
    def wrapper(*args, **kwargs):
        try:
            # Call the original function
            return func(*args, **kwargs)
        except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.ArgumentError) as e:
            # Log the error and return None
            logging.error(f"An error occurred: {e}")
            return None
    return wrapper

# Refactored function to fetch data from postgresql
@handle_db_error  # Use the helper function as a decorator
def fetch_data_from_postgresql(table_name: str = "raw_data", columns: str = "*", import_from_cloud: bool = False) -> pd.DataFrame:
    """Fetch data from postgresql.

    Args:
        table_name (str, optional): The name of the table to fetch. Defaults to "raw_data".
        columns (str, optional): The name of the columns to fetch. Defauts to "*".
        import_from_cloud (bool, optional): Whether to import from the cloud or local database. Defaults to False.

    Returns:
        pd.DataFrame: The dataframe containing the data.
    """
    # Create the database path and the engine
    db_path = create_db_path(import_from_cloud)
    engine = create_db_engine(db_path)
    
    # Establish a connection and execute a query
    with engine.connect() as connection:
        query = f"SELECT {columns} FROM {table_name}"
        df = pd.read_sql_query(query, connection)

    return df

# Refactored function to export dataframe to postgres
@handle_db_error  # Use the helper function as a decorator
def export_dataframe_to_postgresql(df: pd.DataFrame, table_name: str = 'raw_data', if_table_exists: str = 'append', export_to_cloud: bool = False, dtypes:dict = SCRAPE_JOBS_DTYPES) -> None:
    """Export dataframe to postgres.

    Args:
        df (pd.DataFrame): The dataframe to export.
        table_name (str, optional): The name of the table to export. Defaults to 'raw_data'.
        if_table_exists (str, optional): What to do if the table already exists. Defaults to 'append'.
        export_to_cloud (bool, optional): Whether to export to the cloud or local database. Defaults to False.
    """
    # Create the database path and the engine
    db_path = create_db_path(export_to_cloud)
    engine = create_db_engine(db_path)
    
    # Connect to the database
    with engine.connect() as conn:
        # Begin a transaction
        trans = conn.begin()
        try:
            # Use Pandas to_sql with a small subset of the DataFrame
            df.to_sql(table_name, conn, if_exists=if_table_exists, index=False, dtype=dtypes)

            # Commit the transaction
            trans.commit()
            print("✅ Dataframe exported to database")
        except sqlalchemy.exc.IntegrityError as e:
            # Log the error and rollback the transaction
            logging.error(f"An error occurred: {e}")
            trans.rollback()
        # Suppress any other exceptions that are not critical
        with suppress(Exception):
            raise
