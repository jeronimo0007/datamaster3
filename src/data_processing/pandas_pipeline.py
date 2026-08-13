"""
Backend pandas do Medallion — mesmo layout de pastas que o Spark.
Usado pelo Airflow quando PySpark/Java não estão no worker.
"""

from __future__ import annotations

import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from src.data_architecture.medallion import default_layout, landing_dir, project_root
from src.data_processing.dq import assert_dq_gate, run_dq_checks_dict


def _read_landing() -> pd.DataFrame:
    """
    Lê a run mais recente. Os 4 formatos na landing são a *mesma* carga
    (demonstração multi-formato) — escolhe um arquivo, não faz union de todos.
    Preferência: parquet > json > csv > xml > jsonl.
    """
    base = landing_dir()
    runs = sorted([p for p in base.glob("run=*") if p.is_dir()], reverse=True)
    search_roots = runs[:1] if runs else [base]

    def pick(root: Path) -> Path | None:
        for pattern in (
            "**/transactions.parquet",
            "**/transactions.json",
            "**/transactions.csv",
            "**/transactions.xml",
            "**/transactions.jsonl",
        ):
            found = sorted(root.glob(pattern))
            if found:
                return found[0]
        return None

    path = None
    for root in search_roots:
        path = pick(root)
        if path:
            break

    if path is None:
        legacy = project_root() / "data" / "transactions.json"
        if legacy.exists():
            path = legacy
        else:
            raise FileNotFoundError(f"Sem arquivos em {base}")

    suffix = path.suffix.lower()
    if suffix == ".parquet":
        df = pd.read_parquet(path)
    elif suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix == ".jsonl":
        df = pd.read_json(path, lines=True)
    elif suffix == ".xml":
        root_el = ET.parse(path).getroot()
        rows = [{c.tag: c.text for c in tx} for tx in root_el.findall(".//transaction")]
        df = pd.DataFrame(rows)
    else:
        raw = path.read_text(encoding="utf-8").strip()
        data = json.loads(raw)
        df = pd.DataFrame(data if isinstance(data, list) else [data])

    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    if "is_fraud" in df.columns:
        df["is_fraud"] = df["is_fraud"].astype(str).str.lower().isin(["true", "1", "1.0"])
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    print(f"Landing: {len(df)} registros de {path} (formatos irmãos na mesma pasta)")
    return df


def _uri_to_path(uri: str) -> Path:
    if uri.startswith("file:"):
        return Path(uri.replace("file://", ""))
    return Path(uri)


def run_dq_pandas(df: pd.DataFrame) -> dict:
    total = len(df)
    null_amount = int(df["amount"].isna().sum()) if "amount" in df.columns else total
    dupes = (
        int(df["transaction_id"].duplicated().sum()) if "transaction_id" in df.columns else 0
    )
    frauds = int(df["is_fraud"].sum()) if "is_fraud" in df.columns else 0
    return run_dq_checks_dict(
        {
            "total_records": total,
            "null_amount": null_amount,
            "duplicate_ids": dupes,
            "fraud_labeled": frauds,
            "backend": "pandas",
        }
    )


def _reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def run_layer_pandas(layer: str) -> None:
    layout = default_layout()
    bronze_path = _uri_to_path(layout.bronze("transactions"))
    silver_path = _uri_to_path(layout.silver("transactions"))
    gold_path = _uri_to_path(layout.gold("transactions_ml"))
    reports = project_root() / "data" / "lake" / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    if layer in ("bronze", "all"):
        print("=== Bronze (pandas) ===")
        df = _read_landing()
        _reset_dir(bronze_path)
        out = bronze_path / "part-000.parquet"
        df.to_parquet(out, index=False)
        print(f"Bronze: {out}")

    if layer in ("dq", "all"):
        print("=== DQ gate (pandas) ===")
        df = pd.read_parquet(bronze_path / "part-000.parquet")
        dq = run_dq_pandas(df)
        (reports / "dq_latest.json").write_text(json.dumps(dq, indent=2), encoding="utf-8")
        print(json.dumps(dq, indent=2, ensure_ascii=False))
        assert_dq_gate(dq)

    if layer in ("silver", "all"):
        print("=== Silver (pandas) ===")
        df = pd.read_parquet(bronze_path / "part-000.parquet")
        df = df.drop_duplicates(subset=["transaction_id"]) if "transaction_id" in df.columns else df
        df["amount"] = pd.to_numeric(df.get("amount"), errors="coerce").fillna(0).clip(lower=0)
        if "merchant_category" not in df.columns:
            df["merchant_category"] = "UNKNOWN"
        df["merchant_category"] = df["merchant_category"].fillna("UNKNOWN")
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["transaction_date"] = df["timestamp"].dt.strftime("%Y-%m-%d")
        df["transaction_hour"] = df["timestamp"].dt.hour
        df["is_weekend"] = df["timestamp"].dt.dayofweek.isin([5, 6]).astype(int)
        df["is_night"] = df["transaction_hour"].between(0, 5).astype(int)
        if "user_id" in df.columns:
            stats = df.groupby("user_id")["amount"].agg(["mean", "count", "std"]).reset_index()
            stats.columns = ["user_id", "user_avg_amount", "user_total_transactions", "user_amount_stddev"]
            df = df.merge(stats, on="user_id", how="left")
        if "merchant_id" in df.columns:
            mstats = df.groupby("merchant_id")["amount"].agg(["count", "mean"]).reset_index()
            mstats.columns = ["merchant_id", "merchant_transaction_count", "merchant_avg_amount"]
            df = df.merge(mstats, on="merchant_id", how="left")
        _reset_dir(silver_path)
        df.to_parquet(silver_path / "part-000.parquet", index=False)
        print(f"Silver: {silver_path}")

    if layer in ("gold", "all"):
        print("=== Gold (pandas) ===")
        df = pd.read_parquet(silver_path / "part-000.parquet")
        cols = [
            c
            for c in [
                "transaction_id",
                "transaction_date",
                "user_id",
                "amount",
                "merchant_category",
                "is_weekend",
                "is_night",
                "user_avg_amount",
                "user_amount_stddev",
                "merchant_transaction_count",
                "is_fraud",
            ]
            if c in df.columns
        ]
        gold = df[cols]
        if "is_fraud" in gold.columns:
            gold = gold[gold["is_fraud"].notna()]
        _reset_dir(gold_path)
        gold.to_parquet(gold_path / "part-000.parquet", index=False)
        print(f"Gold: {gold_path}")
