import datetime
import pytz
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime.datetime(2023, 6, 16, tzinfo=pytz.timezone("Europe/Paris")),
    'retries': 1,
}

dag = DAG(
    'gg_jobs_search',
    default_args=default_args,
    description='',
    schedule='30 23 * * *',  # Run daily at 23:30
)

task1 = BashOperator(
    task_id='run_scraping_script',
    bash_command='python /home/axel/Documents/gg_job_search/scripts/scraping_jobs.py',
    dag=dag,
)