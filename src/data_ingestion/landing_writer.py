"""Escreve a zona landing em JSON, CSV, Parquet e XML (mesmo schema canônico)."""

from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any

from src.data_architecture.medallion import landing_dir, project_root

CANONICAL_FIELDS = [
    "transaction_id",
    "user_id",
    "merchant_id",
    "amount",
    "merchant_category",
    "payment_method",
    "user_country",
    "merchant_country",
    "timestamp",
    "is_fraud",
    "source",
]


def _run_folder(run_id: str | None = None) -> Path:
    rid = run_id or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = landing_dir() / f"run={rid}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(records: list[dict[str, Any]], folder: Path) -> Path:
    path = folder / "transactions.json"
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_csv(records: list[dict[str, Any]], folder: Path) -> Path:
    path = folder / "transactions.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in records:
            writer.writerow({k: row.get(k) for k in CANONICAL_FIELDS})
    return path


def write_xml(records: list[dict[str, Any]], folder: Path) -> Path:
    path = folder / "transactions.xml"
    root = ET.Element("transactions")
    for row in records:
        tx = ET.SubElement(root, "transaction")
        for key in CANONICAL_FIELDS:
            el = ET.SubElement(tx, key)
            val = row.get(key)
            el.text = "" if val is None else str(val)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path


def write_parquet(records: list[dict[str, Any]], folder: Path) -> Path:
    """Parquet via pandas/pyarrow; se faltar engine, gera CSV tipado + JSONL."""
    path = folder / "transactions.parquet"
    try:
        import pandas as pd

        df = pd.DataFrame([{k: r.get(k) for k in CANONICAL_FIELDS} for r in records])
        df.to_parquet(path, index=False)
        return path
    except Exception as exc:
        print(f"aviso: Parquet indisponível ({exc}); gerando JSONL + instalável via pyarrow")
        alt = folder / "transactions.jsonl"
        with alt.open("w", encoding="utf-8") as f:
            for row in records:
                f.write(json.dumps({k: row.get(k) for k in CANONICAL_FIELDS}, ensure_ascii=False) + "\n")
        # também grava um .parquet marker? melhor tentar pyarrow isolado
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq

            table = pa.Table.from_pylist([{k: r.get(k) for k in CANONICAL_FIELDS} for r in records])
            pq.write_table(table, path)
            return path
        except Exception:
            return alt


def write_multi_format_landing(
    records: list[dict[str, Any]],
    run_id: str | None = None,
) -> dict[str, Path]:
    folder = _run_folder(run_id)
    # também atualiza JSON legado para batch_dataprep_mongo / API
    legacy = project_root() / "data" / "transactions.json"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "json": write_json(records, folder),
        "csv": write_csv(records, folder),
        "parquet": write_parquet(records, folder),
        "xml": write_xml(records, folder),
        "legacy_json": legacy,
    }
