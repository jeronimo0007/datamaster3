"""
DAG Medallion profissional: Bronze → DQ gate → Silver → Gold.

Cada camada é uma task isolada (reprocessável). DQ falhou = Silver/Gold não rodam.
Na Azure/AWS: o mesmo Airflow (ou o mesmo job por camada) — mesmo contrato Medallion.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT = Path("/opt/airflow/project")
PYTHON = "python3"
JOB = f"{PROJECT}/scripts/medallion_job.py"

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="medallion_pipeline",
    description="Orquestra Bronze → DQ → Silver → Gold (Spark local[*])",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["medallion", "spark", "lake"],
) as dag:
    env_exports = (
        f"export PROJECT_ROOT={PROJECT} && "
        f"export PYTHONPATH={PROJECT} && "
        f"export SPARK_MASTER_URL=local[*] && "
        f"cd {PROJECT}"
    )

    bronze = BashOperator(
        task_id="bronze_landing_to_parquet",
        bash_command=f"{env_exports} && {PYTHON} {JOB} bronze --backend pandas",
    )

    dq = BashOperator(
        task_id="dq_gate",
        bash_command=f"{env_exports} && {PYTHON} {JOB} dq --backend pandas",
    )

    silver = BashOperator(
        task_id="silver_clean_enrich",
        bash_command=f"{env_exports} && {PYTHON} {JOB} silver --backend pandas",
    )

    gold = BashOperator(
        task_id="gold_ml_features",
        bash_command=f"{env_exports} && {PYTHON} {JOB} gold --backend pandas",
    )

    bronze >> dq >> silver >> gold
