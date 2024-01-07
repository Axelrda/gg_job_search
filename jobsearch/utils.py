import sqlite3
import pandas as pd

def fetch_table_data(DB_PATH, table='deduplicated_data'):

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
