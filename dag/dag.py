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
    schedule='00 22 * * *',  # Run daily at 10pm
)

scrape_jobs_task = BashOperator(
    task_id='run_scraping_script',
    bash_command='/home/axel/anaconda3/envs/gg_job_search/bin/python /home/axel/Documents/gg_job_search/scripts/scraping_jobs.py',
    dag=dag,
)

sql_deduplicate_task = BashOperator(
    task_id='run_sql_deduplication_script',
    bash_command='/home/axel/anaconda3/envs/gg_job_search/bin/python /home/axel/Documents/gg_job_search/src/cleaning/sql_deduplication.py',
    dag=dag
)

scrape_jobs_task >> sql_deduplicate_task