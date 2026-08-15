"""
Backend pandas do Medallion — mesmo layout de pastas que o Spark.
Usado pelo Airflow quando PySpark/Java não estão no worker.
Suporta storage local e remoto (ADLS `abfss://` via fsspec/adlfs).
"""

from __future__ import annotations

import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from src.data_architecture.medallion import default_layout, landing_dir, project_root
from src.data_architecture.storage import (
    is_remote,
    list_runs,
    read_parquet as storage_read_parquet,
    rmtree as storage_rmtree,
    to_local_path,
    write_text as storage_write_text,
)
from src.data_processing.dq import assert_dq_gate, run_dq_checks_dict


def _is_remote(path: Path | str) -> bool:
    return is_remote(path)


def _join(base: Path | str, name: str) -> Path | str:
    if _is_remote(base):
        return f"{str(base).rstrip('/')}/{name}"
    return to_local_path(base) / name


def _read_landing() -> pd.DataFrame:
    """
    Lê a run mais recente. Os 4 formatos na landing são a *mesma* carga
    (demonstração multi-formato) — escolhe um arquivo, não faz union de todos.
    Preferência: parquet > json > csv > xml > jsonl.
    Suporta landing remota (ADLS `abfss://`) via fsspec.
    """
    base = landing_dir()
    if _is_remote(base):
        runs = list_runs(str(base))
        search_roots = [Path(r) for r in runs[:1]] or [base]
    else:
        base = Path(base)
        runs = sorted([p for p in base.glob("run=*") if p.is_dir()], reverse=True)
        search_roots = runs[:1] or [base]

    def pick(root: Path | str) -> Path | str | None:
        for pattern in (
            "**/transactions.parquet",
            "**/transactions.json",
            "**/transactions.csv",
            "**/transactions.xml",
            "**/transactions.jsonl",
        ):
            if _is_remote(root):
                import fsspec

                found = sorted(fsspec.glob(f"{str(root).rstrip('/')}/{pattern}"))
            else:
                found = sorted(Path(root).glob(pattern))
            if found:
                return Path(found[0]) if not _is_remote(found[0]) else found[0]
        return None

    path: Path | str | None = None
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

    suffix = Path(str(path)).suffix.lower()
    if suffix == ".parquet":
        df = storage_read_parquet(path) if _is_remote(path) else pd.read_parquet(path)
    elif suffix == ".csv":
        df = pd.read_csv(str(path))
    elif suffix == ".jsonl":
        df = pd.read_json(str(path), lines=True)
    elif suffix == ".xml":
        if _is_remote(path):
            from src.data_architecture.storage import read_bytes

            root_el = ET.fromstring(read_bytes(path))
        else:
            root_el = ET.parse(path).getroot()
        rows = [{c.tag: c.text for c in tx} for tx in root_el.findall(".//transaction")]
        df = pd.DataFrame(rows)
    else:
        if _is_remote(path):
            from src.data_architecture.storage import read_text

            raw = read_text(path).strip()
        else:
            raw = Path(path).read_text(encoding="utf-8").strip()
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


def _reset_dir(path: Path | str) -> None:
    if _is_remote(path):
        storage_rmtree(path)
        from src.data_architecture.storage import makedirs as remote_makedirs

        remote_makedirs(path, exist_ok=True)
    else:
        p = Path(path)
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True, exist_ok=True)


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


def _save_parquet(df: pd.DataFrame, path: Path | str) -> None:
    df.to_parquet(str(path), index=False)


def _read_df(path: Path | str) -> pd.DataFrame:
    if _is_remote(path):
        return storage_read_parquet(path)
    return pd.read_parquet(path)


def _write_report(reports: Path | str, dq: dict) -> None:
    path = _join(reports, "dq_latest.json")
    storage_write_text(path, json.dumps(dq, indent=2))


def run_layer_pandas(layer: str) -> None:
    layout = default_layout()

    def norm(uri: str) -> Path | str:
        return uri if is_remote(uri) else to_local_path(uri)

    bronze_path = norm(layout.bronze("transactions"))
    silver_path = norm(layout.silver("transactions"))
    gold_path = norm(layout.gold("transactions_ml"))
    reports = norm(layout.reports())
    _reset_dir(reports)

    if layer in ("bronze", "all"):
        print("=== Bronze (pandas) ===")
        df = _read_landing()
        _reset_dir(bronze_path)
        out = _join(bronze_path, "part-000.parquet")
        _save_parquet(df, out)
        print(f"Bronze: {out}")

    if layer in ("dq", "all"):
        print("=== DQ gate (pandas) ===")
        df = _read_df(_join(bronze_path, "part-000.parquet"))
        dq = run_dq_pandas(df)
        _write_report(reports, dq)
        print(json.dumps(dq, indent=2, ensure_ascii=False))
        assert_dq_gate(dq)

    if layer in ("silver", "all"):
        print("=== Silver (pandas) ===")
        df = _read_df(_join(bronze_path, "part-000.parquet"))
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
        _save_parquet(df, _join(silver_path, "part-000.parquet"))
        print(f"Silver: {silver_path}")

    if layer in ("gold", "all"):
        print("=== Gold (pandas) ===")
        df = _read_df(_join(silver_path, "part-000.parquet"))
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
        _save_parquet(gold, _join(gold_path, "part-000.parquet"))
        print(f"Gold: {gold_path}")
