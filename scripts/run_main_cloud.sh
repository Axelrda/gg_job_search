LOG_FILE="/home/axelus/gg_job_search/logs/serpapi_scraping.log"

{

echo "[$(date)] Starting the jobsearch script"

echo "[$(date)] Initializing pyenv"
# Initialize pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
fi

#pyenv activate ggjobsearch || { echo "[$(date)] Failed to activate pyenv environment"; exit 1; }
echo "[$(date)] Changing to project directory"
cd $HOME/gg_job_search || { echo "[$(date)] Failed to change directory"; exit 1; }

echo "[$(date)] Sourcing environment variables" >> $LOG_FILE
source $HOME/gg_job_search/cron.env || { echo "[$(date)] Failed to source env var"; exit 1; }

/home/axelus/.pyenv/shims/python -m jobsearch -n 50
echo "[$(date)] Script finished"

} >> $LOG_FILE 2>&1
