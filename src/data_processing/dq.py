"""Data Quality gate — falha impede avanço Bronze → Silver."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.data_architecture.medallion import MedallionLayout, default_layout, project_root


def run_dq_checks_dict(stats: dict[str, Any]) -> dict:
    """Monta relatório a partir de métricas já calculadas (Spark ou pandas)."""
    total = int(stats.get("total_records", 0))
    null_amount = int(stats.get("null_amount", 0))
    dupes = int(stats.get("duplicate_ids", 0))
    frauds = int(stats.get("fraud_labeled", 0))
    return {
        "validation_time": datetime.utcnow().isoformat(),
        "total_records": total,
        "null_amount": null_amount,
        "duplicate_ids": dupes,
        "fraud_labeled": frauds,
        "fraud_rate": round(frauds / total, 4) if total else 0,
        "success": total > 0 and null_amount == 0 and dupes == 0,
        **{k: v for k, v in stats.items() if k not in {"total_records", "null_amount", "duplicate_ids", "fraud_labeled"}},
    }


def run_dq_checks(df) -> dict:
    """DQ sobre DataFrame Spark (import tardio)."""
    from pyspark.sql.functions import col

    total = df.count()
    null_amount = df.filter(col("amount").isNull()).count() if "amount" in df.columns else total
    if "transaction_id" in df.columns:
        dupes = total - df.dropDuplicates(["transaction_id"]).count()
    else:
        dupes = 0
    frauds = (
        df.filter(col("is_fraud") == True).count()  # noqa: E712
        if "is_fraud" in df.columns
        else 0
    )
    return run_dq_checks_dict(
        {
            "total_records": total,
            "null_amount": null_amount,
            "duplicate_ids": dupes,
            "fraud_labeled": frauds,
            "backend": "spark",
        }
    )


def write_dq_report(dq: dict, layout: MedallionLayout | None = None) -> Path:
    layout = layout or default_layout()
    root = project_root()
    path = root / "data" / "lake" / "reports" / "dq_latest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dq, indent=2), encoding="utf-8")
    print(f"DQ report: {path}")
    return path


def assert_dq_gate(dq: dict) -> None:
    """Gate: lança erro se DQ falhar — Airflow marca a task como failed."""
    if not dq.get("success"):
        raise ValueError(
            f"DQ gate falhou: null_amount={dq.get('null_amount')} "
            f"duplicates={dq.get('duplicate_ids')} total={dq.get('total_records')}"
        )
