
# start google cloud proxy from ggjobsearch dir (need env vars)
cd /home/axelus/data_science_projects/gg_job_search
# launch it from tmux 
tmux
# start proxy (and then ctrl - b + d)
~/cloud-sql-proxy --port=5433 --credentials-file=$GOOGLE_APPLICATION_CREDENTIALS $GOOGLE_SQL_INSTANCE_CONNECTION_NAME

# fetch new data and export to local

psql -h localhost -p 5433 -U postgres -d ggjobsearch -c "\copy (SELECT * FROM raw_data WHERE local_sync_timestamp IS NULL) TO STDOUT" | psql -h localhost -p 5432 -U postgres -d ggjobsearch -c "\copy raw_data FROM STDIN"

# update cloud then local db
psql -h localhost -p 5433 -U postgres -d ggjobsearch -c "UPDATE raw_data SET local_sync_timestamp = CURRENT_TIMESTAMP WHERE local_sync_timestamp IS NULL"
psql -h localhost -p 5432 -U postgres -d ggjobsearch -c "UPDATE raw_data SET local_sync_timestamp = CURRENT_TIMESTAMP WHERE local_sync_timestamp IS NULL"