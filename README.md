# Airflow + Astronomer Cosmos (Sanima Bank dbt)

This project runs Apache Airflow 3.3.2 in Docker. It uses [Astronomer Cosmos](https://github.com/astronomer/astronomer-cosmos) to turn the `sanima-bank-dbt` dbt project into an Airflow DAG, where each dbt model, seed and snapshot runs as its own Airflow task.

## Project layout

```
.
├── Dockerfile              # Airflow image + Cosmos + dbt (in a separate venv)
├── docker-compose.yaml     # Airflow services, builds the image from the Dockerfile
├── .env                    # FERNET_KEY and AIRFLOW_UID (not committed)
├── dags/
│   ├── dbt_sanima_cosmos.py   # Cosmos DbtDag for the Sanima Bank dbt project
│   └── ...                    # other practice DAGs
├── sanima-bank-dbt/        # dbt project (staging → silver, marts → gold)
├── config/  logs/  plugins/
```

## How it works

- **Cosmos** is installed in Airflow's own Python environment.
- **dbt-postgres** is installed in a separate virtualenv at `/opt/airflow/dbt_venv`, so its dependencies can't clash with Airflow's.
- The dbt project is mounted into the containers at `/opt/airflow/dbt/sanima-bank-dbt`.
- Cosmos builds dbt's `profiles.yml` at runtime from the Airflow connection `sanima_postgres`. The `profiles.yml` inside the dbt project is only used when you run dbt locally.
- The `sanima_postgres` connection points to the Postgres server running on your **host machine** (`host.docker.internal:5432`). That is where the raw Sanima Bank tables live.

## Prerequisites

- Docker Desktop (or Docker Engine + Compose v2), with at least 4 GB of memory allocated
- A Postgres server on your machine on port `5432` (user `postgres`, password `postgres`), with the raw source tables in the `public` schema of the `postgres` database
  - Create and load them with the scripts in `sanima-bank-dbt/SQL FILES/` (start with `insert.sql`)

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Prashanta443/astronomer-cosmos.git
cd astronomer-cosmos
```

### 2. Create the `.env` file

Generate a Fernet key:

```bash
# macOS / Linux
python3 -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"

# Windows
python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
```

Create `.env` in the project root:

```env
FERNET_KEY=<paste-the-generated-key>
AIRFLOW_UID=50000
```

On Linux, set `AIRFLOW_UID` to the output of `id -u` so that files in `logs/` are owned by your user.

### 3. Create the local folders

```bash
mkdir -p ./dags ./logs ./plugins ./config
```

### 4. Build the image

The Dockerfile extends `apache/airflow:3.3.2`, installs `astronomer-cosmos`, and creates the dbt venv with `dbt-postgres`:

```bash
docker compose build
```

The built image is tagged `sanima-airflow-cosmos:3.3.2`. Rebuild it whenever you change the Dockerfile.

### 5. Initialise Airflow

```bash
docker compose up airflow-init
```

### 6. Start Airflow

```bash
docker compose up -d
```

Open http://localhost:8080 and log in with `airflow` / `airflow`.

### 7. Check the Postgres connection

The connection is defined in `docker-compose.yaml` as an environment variable, so you don't need to create it in the UI:

```yaml
AIRFLOW_CONN_SANIMA_POSTGRES: '{"conn_type": "postgres", "host": "host.docker.internal", "port": 5432, "login": "postgres", "password": "postgres", "schema": "postgres"}'
```

If your local Postgres uses different credentials, change them there and run `docker compose up -d` again.

### 8. Run the dbt DAG

In the Airflow UI, find the DAG **`dbt_astomermer_cosmos`** (tags: `dbt`, `cosmos`). It has no schedule, so trigger it manually.

Cosmos renders one task group per dbt node:

- **seeds** – `currency_conversion_rates`
- **staging** models → `silver` schema
- **marts** models (`dim_card`, `dim_product`, `fct_casa_ratio`, `fct_loan_to_deposit_ratio`) → `gold` schema
- tests run after each model (`TestBehavior.AFTER_EACH`)

`max_active_tasks=1` makes the tasks run one at a time.

## Running dbt locally (optional)

```bash
cd sanima-bank-dbt
python -m venv env && source env/bin/activate
pip install dbt-postgres
dbt debug --profiles-dir .
dbt build --profiles-dir .
```

## Useful commands

```bash
docker compose ps                         # container status
docker compose logs -f airflow-scheduler  # follow scheduler logs
docker compose down                       # stop
docker compose down -v                    # stop and delete the Airflow metadata DB
```

The Airflow metadata Postgres is exposed on host port `5435`, so it doesn't conflict with your local Postgres on `5432`.

## Troubleshooting

| Problem | Fix |
|---|---|
| DAG doesn't appear | Check `docker compose logs airflow-dag-processor` for import errors. Make sure the image was rebuilt so `cosmos` is installed. |
| `dbt executable not found` | Rebuild the image: `docker compose build --no-cache`. |
| Connection refused to Postgres | Make sure local Postgres is listening on `5432` and accepts connections from Docker (`listen_addresses = '*'` and a `pg_hba.conf` entry). |
| Source table not found | Load the raw tables with the scripts in `sanima-bank-dbt/SQL FILES/`. |
