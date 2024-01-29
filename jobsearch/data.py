import sqlite3
from sqlalchemy import create_engine
from jobsearch.params import *
import pandas as pd

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
