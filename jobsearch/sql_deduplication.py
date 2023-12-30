import sqlite3
# necessary for path to files
from config import DB_PATH



def deduplicate_data(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # Start a transaction
        c.execute('BEGIN TRANSACTION;')

        c.execute('DROP TABLE IF EXISTS deduplicated_data;')

        c.execute('''
            CREATE TABLE deduplicated_data AS
                SELECT title, company_name, location, via, description, job_highlights, related_links, thumbnail, extensions, job_id, posted_at, schedule_type, date_time, search_query
                FROM (
                    SELECT *,
                    ROW_NUMBER() OVER(PARTITION BY description) AS rn
                    FROM unprocessed_data
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
        # Close the connection
        conn.close()