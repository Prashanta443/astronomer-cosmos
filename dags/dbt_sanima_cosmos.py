import pendulum

from cosmos import DbtDag, ExecutionConfig, ProfileConfig, ProjectConfig, RenderConfig
from cosmos.constants import TestBehavior
from cosmos.profiles import PostgresUserPasswordProfileMapping

DBT_PROJECT_PATH = "/opt/airflow/dbt/sanima-bank-dbt"
DBT_EXECUTABLE_PATH = "/opt/airflow/dbt_venv/bin/dbt"

# Cosmos builds profiles.yml at runtime from the Airflow connection,
# so the localhost settings in the project's profiles.yml are not used here.
profile_config = ProfileConfig(
    profile_name="dbt_proj",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="sanima_postgres",
        profile_args={"schema": "public"},
    ),
)

sanima_bank_dbt = DbtDag(
    dag_id="dbt_astomermer_cosmos",
    project_config=ProjectConfig(DBT_PROJECT_PATH),
    profile_config=profile_config,
    execution_config=ExecutionConfig(dbt_executable_path=DBT_EXECUTABLE_PATH),
    # Skip dbt tests in Airflow; only seeds, snapshots and models run
    render_config=RenderConfig(test_behavior=TestBehavior.AFTER_EACH),
    # dbt package install gardoina
    operator_args={"install_deps": False},
    # 1 task matra run hunxa at one time
    max_active_tasks=1,
    schedule=None,
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),
    catchup=False,
    tags=["dbt", "cosmos", "test"],
)
