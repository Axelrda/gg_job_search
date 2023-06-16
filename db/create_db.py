import sqlite3

# Connect to SQLite and create a new database (or open it if it already exists)
conn = sqlite3.connect('jobs_database.db')

# read pandas dataframe
#df = pd.read_csv('data/unprocessed_data.csv')
# Write the data of a pandas DataFrame into a SQL database
#df.to_sql('unprocessed_data', conn, if_exists='replace', index=False)

cursor = conn.cursor()

cursor.execute("""

    SELECT name FROM sqlite_master WHERE type='table';

""")

# Fetch all the rows returned by the query
table_names = cursor.fetchall()

# Print the table names
for name in table_names:
    print(name[0])
    

