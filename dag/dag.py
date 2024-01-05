import datetime
import pytz
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime.datetime(2024, 1, 3, tzinfo=pytz.timezone("Europe/Paris")),
    'retries': 1,
}

dag = DAG(
    'ggjobsearch',
    default_args=default_args,
    description='',
    schedule='05 23 * * *',  # Run daily at 10pm
)

scrape_jobs_task = BashOperator(
    task_id='run_scraping_script',
    bash_command='/home/axelus/anaconda3/envs/ggjobsearch/bin/python /home/axelus/data_science_projects/gg_job_search/jobsearch/scraping_jobs.py',
    dag=dag,
)

sql_deduplicate_task = BashOperator(
    task_id='run_sql_deduplication_script',
    bash_command='/home/axelus/anaconda3/envs/ggjobsearch/bin/python /home/axelus/data_science_projects/gg_job_search/jobsearch/sql_deduplication.py',
    dag=dag
)

scrape_jobs_task >> sql_deduplicate_task
