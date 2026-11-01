
from datetime import datetime

from airflow.sdk import dag, task
from airflow.providers.standard.operators.python import BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule


@dag(
    dag_id="branch_python_operator_dag",
    description="Airflow DAG using @dag, @task and BranchPythonOperator",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["airflow", "branching"],
)
def branch_python_operator_example():

    @task
    def generate_quality_score() -> int:
        score = 85
        print(f"Generated data quality score: {score}")
        return score

    def choose_branch(score: int) -> str:
        if score >= 80:
            return "data_quality_passed"
        return "data_quality_failed"

    score = generate_quality_score()

    branch = BranchPythonOperator(
        task_id="choose_data_quality_branch",
        python_callable=choose_branch,
        op_args=[score],
    )

    @task
    def data_quality_passed():
        print("Quality passed. Continue the ETL pipeline.")

    @task
    def data_quality_failed():
        print("Quality failed. Notify the data engineering team")

    @task(trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
    def finish_pipeline():
        print("Pipeline finished.")

    passed = data_quality_passed()
    failed = data_quality_failed()
    finish = finish_pipeline()

    branch >> [passed, failed]
    [passed, failed] >> finish


branch_python_operator_example()


