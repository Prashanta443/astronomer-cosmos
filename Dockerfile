FROM apache/airflow:3.3.2

# Cosmos runs inside Airflow's own Python environment
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" astronomer-cosmos

# dbt goes into a separate venv so its dependencies can't clash with Airflow's
RUN python -m venv /opt/airflow/dbt_venv && \
    /opt/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-postgres

