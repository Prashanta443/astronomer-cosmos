from datetime import timedelta
from pendulum import datetime

from airflow.sdk import dag,task
from airflow.providers.standard.operators.empty import EmptyOperator


@dag(
    dag_id = 'scheduling_task',
    schedule = '20 7 * * *',
    start_date = datetime(2026,9,21, tz = "Asia/Kathmandu"),
    catchup = False,
    is_paused_upon_creation = False,
    tags = ['scheduling airflow dag'],
    max_active_runs = 1
)

def schedule_dag():
    @task.python(
        retries = 3,
        retry_delay = timedelta(minutes = 3)
    )
    def first_task():
        print("print hello from python")
    
    @task.bash
    def processing_data():
        return "echo 'Hello from bash task operator!'"
    
    end = EmptyOperator(
        task_id = "task_end"
    )

    start = first_task()
    process = processing_data()

    start >> process >> end 


schedule_dag()

