import sqlite3
# necessary for path to files
from params import DB_PATH



def deduplicate_data(DB_PATH):
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
        print("Closing database ...")
        # Close the connection
        conn.close()

if __name__ == "__main__":
    deduplicate_data(DB_PATH)
