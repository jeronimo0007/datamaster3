"""
DAG: ingestão multi-formato (JSON, CSV, Parquet, XML) → zona landing.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

PROJECT = Path("/opt/airflow/project")


def _run_ingest(**_context):
    import sys

    sys.path.insert(0, str(PROJECT))
    from src.data_ingestion.landing_writer import write_multi_format_landing
    from src.data_ingestion.public_fraud_sources import collect_fraud_records

    records = collect_fraud_records(n_synthetic=400, fetch_public=True)
    paths = write_multi_format_landing(records)
    for fmt, path in paths.items():
        print(f"{fmt}: {path}")


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="ingest_multi_source",
    description="Ingestão API pública + sintético em JSON/CSV/Parquet/XML",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["ingest", "landing", "fraud"],
) as dag:
    ingest = PythonOperator(
        task_id="collect_and_land_four_formats",
        python_callable=_run_ingest,
    )

    # Espelho opcional para batch Mongo (serving da API)
    prep_mongo = BashOperator(
        task_id="batch_profiles_mongo",
        bash_command=(
            f"cd {PROJECT} && "
            "python3 scripts/batch_dataprep_mongo.py -i data/transactions.json || "
            "echo 'Mongo batch opcional — ignore se Mongo indisponível no worker'"
        ),
    )

    ingest >> prep_mongo
