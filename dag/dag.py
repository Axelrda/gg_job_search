import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime.datetime(2023, 6, 16),
    'retries': 1,
}

dag = DAG(
    'my_dag',
    default_args=default_args,
    description='',
    schedule_interval='30 23 * * *',  # Run daily at 23:30
)

task1 = BashOperator(
    task_id='run_scraping_script',
    bash_command='python scripts/scraping_jobs.py',
    dag=dag,
)