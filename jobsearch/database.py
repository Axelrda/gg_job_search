import pandas as pd

import sqlite3
from sqlalchemy import create_engine

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

def deduplicate_sqlite_data(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    print(DB_PATH)
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

def fetch_data_from_local_sqlite(DB_PATH, table='raw_data'):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30)
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


def fetch_data_from_local_postgresql(table="raw_data"):
    try:
        engine = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_LOCALHOST}/{POSTGRES_DATABASE}')

        # Establish a connection and execute a query
        with engine.connect() as connection:
            query = f"SELECT * FROM {table}"
            df = pd.read_sql_query(query, connection)

    except Exception as e:
        print("An error occurred:", e)
        df = None

    return df

def export_to_sqlite(DB_PATH, all_jobs):
    #### EXPORT TO SQLITE DATABASE ####
    # convert value to str format (sql database doesn't accept list type)
    for column in all_jobs.columns:
        all_jobs[column] = all_jobs[column].apply(lambda x: str(x) if isinstance(x, list) else x)

    print("Now, exporting data to SQL database ...")

    # export data to database
    with sqlite3.connect(DB_PATH) as conn:
        all_jobs.to_sql('raw_data', conn, if_exists='append', index=False)

    print("Data exported ✅")

def export_dataframe_to_postgres(df, table_name='raw_data', if_table_exists='append'):
    # import params.py first
    print("Now, exporting data to postgres database ...")
    gcs_db_path = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_GCS_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'
    engine = create_engine(gcs_db_path)

    # Connect to the database
    with engine.connect() as conn:
        # Begin a transaction
        trans = conn.begin()
        try:
            # Use Pandas to_sql with a small subset of the DataFrame
            df.to_sql(table_name, conn, if_exists=if_table_exists, index=False)

            # Commit the transaction
            trans.commit()
            print("✅ Dataframe exported to postgres database")
        except Exception as e:
            print("An error occurred:", e)
            trans.rollback()  # Rollback the transaction in case of error
