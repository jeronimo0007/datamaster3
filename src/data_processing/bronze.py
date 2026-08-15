"""Camada Bronze: landing multi-formato → Parquet bruto no lake."""

from __future__ import annotations

import json
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, to_timestamp

from src.data_architecture.medallion import MedallionLayout, default_layout, landing_dir, project_root


def _read_json_flexible(spark: SparkSession, path: Path) -> DataFrame:
    raw = path.read_text(encoding="utf-8").strip()
    if raw.startswith("["):
        records = json.loads(raw)
        if not records:
            raise ValueError(f"JSON vazio: {path}")
        return spark.createDataFrame(records)
    return spark.read.json(str(path))


def read_landing(spark: SparkSession, landing: Path | str | None = None) -> DataFrame:
    """
    Lê a run mais recente da landing.
    Os 4 formatos são a mesma carga (demo multi-formato) — escolhe um arquivo.
    Preferência: parquet > json > csv > xml.
    Suporta landing remota (ADLS `abfss://`) via fsspec.
    """
    from src.data_architecture.storage import is_remote, list_runs

    root = project_root()
    base = landing if landing is not None else landing_dir(root)
    remote = is_remote(base)
    if remote:
        runs = list_runs(str(base))
        search = Path(runs[0]) if runs else Path(str(base))
    else:
        runs = sorted([p for p in Path(base).glob("run=*") if p.is_dir()], reverse=True)
        search = runs[0] if runs else Path(base)

    chosen: Path | str | None = None
    for pattern in (
        "**/transactions.parquet",
        "**/transactions.json",
        "**/transactions.csv",
        "**/transactions.xml",
        "**/transactions.jsonl",
    ):
        if remote:
            import fsspec

            found = sorted(fsspec.glob(f"{str(search).rstrip('/')}/{pattern}"))
        else:
            found = sorted(Path(search).glob(pattern))
        if found:
            chosen = found[0]
            break

    if chosen is None:
        legacy = root / "data" / "transactions.json"
        if legacy.exists():
            chosen = legacy
        else:
            raise FileNotFoundError(
                f"Nenhum arquivo em {base}. Rode a DAG de ingestão ou scripts/ingest_landing.py."
            )

    if remote:
        from src.data_architecture.storage import read_bytes, read_text

        suffix = Path(str(chosen)).suffix.lower()
        if suffix == ".parquet":
            df = spark.read.parquet(str(chosen))
        elif suffix == ".csv":
            df = spark.read.option("header", True).option("inferSchema", True).csv(str(chosen))
        elif suffix == ".jsonl":
            df = spark.read.json(str(chosen))
        elif suffix == ".xml":
            import pandas as pd

            root_el = ET.fromstring(read_bytes(chosen))
            rows = [{child.tag: child.text for child in tx} for tx in root_el.findall(".//transaction")]
            df = spark.createDataFrame(pd.DataFrame(rows))
        else:
            raw = read_text(chosen).strip()
            if raw.startswith("["):
                df = spark.createDataFrame(json.loads(raw))
            else:
                df = spark.read.json(str(chosen))
    else:
        suffix = Path(chosen).suffix.lower()
        if suffix == ".parquet":
            df = spark.read.parquet(str(chosen))
        elif suffix == ".csv":
            df = spark.read.option("header", True).option("inferSchema", True).csv(str(chosen))
        elif suffix == ".xml":
            import pandas as pd

            root_el = ET.parse(chosen).getroot()
            rows = [{child.tag: child.text for child in tx} for tx in root_el.findall(".//transaction")]
            df = spark.createDataFrame(pd.DataFrame(rows))
        elif suffix == ".jsonl":
            df = spark.read.json(str(chosen))
        else:
            df = _read_json_flexible(spark, chosen)

    if "timestamp" in df.columns:
        df = df.withColumn("timestamp", to_timestamp(col("timestamp")))

    print(f"Bronze input: {df.count()} registros de {chosen}")
    return df


def write_bronze(df: DataFrame, layout: MedallionLayout | None = None) -> str:
    layout = layout or default_layout()
    out = layout.bronze("transactions")
    df.write.mode("overwrite").parquet(out)
    print(f"Bronze Parquet: {out}")
    return out


def run_bronze(spark: SparkSession, layout: MedallionLayout | None = None) -> DataFrame:
    layout = layout or default_layout()
    df = read_landing(spark)
    write_bronze(df, layout)
    return spark.read.parquet(layout.bronze("transactions"))
