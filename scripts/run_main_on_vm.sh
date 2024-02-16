#!/bin/zsh

LOG_FILE="$HOME/data_science_projects/gg_job_search/logs/serpapi_scraping.log"

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
    cd $HOME/data_science_projects/gg_job_search || { echo "[$(date)] Failed to change directory"; exit 1; }

    echo "[$(date)] Sourcing environment variables"
    source $HOME/data_science_projects/gg_job_search/cron.env || { echo "[$(date)] Failed to source env var"; exit 1; }

    # # Automatically export all variables that are defined or modified
    # set -a
    # # Source the .env file. Variables in this file are automatically exported.
    # source $HOME/data_science_projects/gg_job_search/cron.env
    # # Revert to normal behavior; no longer auto-export variables
    # set +a

    echo "[$(date)] Running the Python script"
    /home/axelus/anaconda3/envs/ggjobsearch/bin/python -m jobsearch -n 1

    echo "[$(date)] Script finished"

} >> "$LOG_FILE" 2>&1
