#!/bin/zsh

PROJECT_PATH="$HOME/data_science_projects/gg_job_search"
DB_PATH=$PROJECT_PATH/db/jobs_database.db
LOGFILE="$PROJECT_PATH/logs/run_full_pipeline.log"
ENV_FILE="$PROJECT_PATH/.env"
TEMP_ENV_FILE="$PROJECT_PATH/temp_env.sh"

# Logging initialization
echo "$(date): Initializing script" >> "$LOGFILE"

# Initialize conda
echo "$(date): Sourcing Conda" >> "$LOGFILE"
source ~/anaconda3/etc/profile.d/conda.sh >> "$LOGFILE" 2>&1

# Activate environment
echo "$(date): Activating Conda environment" >> "$LOGFILE"
conda activate ggjobsearch >> "$LOGFILE" 2>&1

# Create a temporary .env file with 'export' prepended to each line
echo "$(date): Creating temporary .env file" >> "$LOGFILE"
sed 's/^/export /' $ENV_FILE > $TEMP_ENV_FILE 2>> "$LOGFILE"

# Source the temporary environment variables
echo "$(date): Sourcing temporary environment variables" >> "$LOGFILE"
source $TEMP_ENV_FILE >> "$LOGFILE" 2>&1

echo "$(date): Starting full pipeline script" >> "$LOGFILE"

# launch scraping
echo "$(date): Starting job scraping" >> "$LOGFILE"
python $PROJECT_PATH/jobsearch/scraping_jobs.py >> "$LOGFILE" 2>&1

# launch 1st deduplication
echo "$(date): Starting deduplication" >> "$LOGFILE"
python $PROJECT_PATH/jobsearch/sql_deduplication.py >> "$LOGFILE" 2>&1

# get statistics
echo "$(date): Getting database statistics" >> "$LOGFILE"

RAW_COUNT=$(echo "SELECT COUNT(*) FROM unprocessed_data;" | sqlite3 $DB_PATH)
CLEAN_COUNT=$(echo "SELECT COUNT(*) FROM deduplicated_data;" | sqlite3 $DB_PATH)

echo "Total raw records : $RAW_COUNT" >> "$LOGFILE"
echo "Total cleaned records : $CLEAN_COUNT" >> "$LOGFILE"


# removing temporary modified env file
rm $TEMP_ENV_FILE

echo "$(date): Script completed" >> "$LOGFILE"
