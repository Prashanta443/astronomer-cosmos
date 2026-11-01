from datetime import timedelta
from pendulum import datetime

from airflow.sdk import dag,task
from airflow.providers.standard.operators.empty import EmptyOperator


@dag(
    dag_id = 'first_class_dag',
    schedule = None,
    start_date = datetime(2026,9,21,tz ="Asia/Kathmandu"),
    catchup = False,
    tags =["first class",'learn airflow']
)
def normal_dag_first_class():
    @task.python
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

normal_dag_first_class()