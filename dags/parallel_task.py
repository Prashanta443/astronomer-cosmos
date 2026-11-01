from datetime import timedelta
from pendulum import datetime

from airflow.sdk import dag,task
from airflow.providers.standard.operators.empty import EmptyOperator



@dag(
    dag_id = 'parallel_task_execution',
    schedule = None,
    start_date = datetime(2026,9,21,tz ="Asia/Kathmandu"),
    catchup = False,
    tags =["parallel task",'learn airflow']
)

def parallel_task_execution():
    
    start = EmptyOperator(
        task_id = "starting_task"
    )

    @task
    def ingest_from_api():
        print("ingesting data from api")
        return  {
                "userId": 1,
                "id": 1,
                "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
                "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
        }

    @task
    def creating_table():
        print("creating table ")
        print("table created")

    @task
    def loading_data(data):
        print("loadfing data",data)

    api_data = ingest_from_api()
    creating_table_data = creating_table()
    load_data = loading_data(api_data)

    
    start >>[ api_data,creating_table_data] >> load_data

parallel_task_execution()

    

    



