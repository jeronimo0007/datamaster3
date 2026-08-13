"""
DAG ponta a ponta: ingestão → Medallion completo.
Útil para demo da banca em um único Trigger.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 0,
}

with DAG(
    dag_id="datamaster_e2e",
    description="Trigger: ingest_multi_source → medallion_pipeline",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["e2e", "demo", "banca"],
) as dag:
    ingest = TriggerDagRunOperator(
        task_id="trigger_ingest",
        trigger_dag_id="ingest_multi_source",
        wait_for_completion=True,
        poke_interval=10,
        reset_dag_run=True,
    )

    medallion = TriggerDagRunOperator(
        task_id="trigger_medallion",
        trigger_dag_id="medallion_pipeline",
        wait_for_completion=True,
        poke_interval=10,
        reset_dag_run=True,
    )

    ingest >> medallion
