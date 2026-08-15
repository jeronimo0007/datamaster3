"""Escreve a zona landing em JSON, CSV, Parquet e XML (mesmo schema canônico)."""

from __future__ import annotations

import csv
import io
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any

from src.data_architecture.medallion import landing_dir, project_root
from src.data_architecture.storage import (
    is_remote,
    makedirs,
    to_local_path,
    write_bytes,
    write_parquet as _write_parquet_remote,
    write_text,
)

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


def _is_remote(path: Path | str) -> bool:
    return is_remote(path)


def _join(base: Path | str, name: str) -> Path | str:
    """Junta nome ao folder preservando URI remota (abfss:// não vira abfss:/)."""
    if _is_remote(base):
        return f"{str(base).rstrip('/')}/{name}"
    return to_local_path(base) / name


def _write_text(path: Path | str, content: str, encoding: str = "utf-8") -> None:
    if _is_remote(path):
        write_text(path, content, encoding=encoding)
    else:
        Path(path).write_text(content, encoding=encoding)


def _run_folder(run_id: str | None = None) -> Path | str:
    rid = run_id or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = _join(landing_dir(), f"run={rid}")
    makedirs(path, exist_ok=True)
    return path


def write_json(records: list[dict[str, Any]], folder: Path | str) -> Path | str:
    path = _join(folder, "transactions.json")
    _write_text(path, json.dumps(records, ensure_ascii=False, indent=2))
    return path


def write_csv(records: list[dict[str, Any]], folder: Path | str) -> Path | str:
    path = _join(folder, "transactions.csv")
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=CANONICAL_FIELDS, extrasaction="ignore")
    writer.writeheader()
    for row in records:
        writer.writerow({k: row.get(k) for k in CANONICAL_FIELDS})
    _write_text(path, buf.getvalue())
    return path


def write_xml(records: list[dict[str, Any]], folder: Path | str) -> Path | str:
    path = _join(folder, "transactions.xml")
    root = ET.Element("transactions")
    for row in records:
        tx = ET.SubElement(root, "transaction")
        for key in CANONICAL_FIELDS:
            el = ET.SubElement(tx, key)
            val = row.get(key)
            el.text = "" if val is None else str(val)
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    write_bytes(path, xml_bytes)
    return path


def write_parquet(records: list[dict[str, Any]], folder: Path | str) -> Path | str:
    """Parquet via pandas/pyarrow; se faltar engine, gera CSV tipado + JSONL."""
    path = _join(folder, "transactions.parquet")
    try:
        import pandas as pd

        df = pd.DataFrame([{k: r.get(k) for k in CANONICAL_FIELDS} for r in records])
        if _is_remote(path):
            _write_parquet_remote(df, str(path), index=False)
        else:
            df.to_parquet(path, index=False)
        return path
    except Exception as exc:
        print(f"aviso: Parquet indisponível ({exc}); gerando JSONL + instalável via pyarrow")
        alt = _join(folder, "transactions.jsonl")
        _write_text(alt, "\n".join(
            json.dumps({k: row.get(k) for k in CANONICAL_FIELDS}, ensure_ascii=False)
            for row in records
        ) + "\n")
        # também grava um .parquet marker? melhor tentar pyarrow isolado
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq

            table = pa.Table.from_pylist([{k: r.get(k) for k in CANONICAL_FIELDS} for r in records])
            pq.write_table(table, str(path))
            return path
        except Exception:
            return alt


def write_metadata_json(metadata: dict[str, Any], folder: Path | str) -> Path | str:
    """Grava metadados de fonte pública (API OpenML) na landing — proveniência."""
    path = _join(folder, "source_metadata.json")
    _write_text(path, json.dumps(metadata, ensure_ascii=False, indent=2))
    return path


def write_multi_format_landing(
    records: list[dict[str, Any]],
    run_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Path | str]:
    folder = _run_folder(run_id)
    # também atualiza JSON legado para batch_dataprep_mongo / API
    legacy = project_root() / "data" / "transactions.json"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    out = {
        "json": write_json(records, folder),
        "csv": write_csv(records, folder),
        "parquet": write_parquet(records, folder),
        "xml": write_xml(records, folder),
        "legacy_json": legacy,
    }
    if metadata:
        out["metadata_json"] = write_metadata_json(metadata, folder)
    return out
