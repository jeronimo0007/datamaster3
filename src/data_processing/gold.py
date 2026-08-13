"""Camada Gold: features ML / consumo analítico."""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col

from src.data_architecture.medallion import MedallionLayout, default_layout

GOLD_FEATURE_COLS = [
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


def to_gold_features(df: DataFrame) -> DataFrame:
    cols = [c for c in GOLD_FEATURE_COLS if c in df.columns]
    gold = df.select(*cols)
    if "is_fraud" in gold.columns:
        gold = gold.filter(col("is_fraud").isNotNull())
    return gold


def write_gold(df: DataFrame, layout: MedallionLayout | None = None) -> str:
    layout = layout or default_layout()
    out = layout.gold("transactions_ml")
    df.write.mode("overwrite").partitionBy("transaction_date").parquet(out)
    print(f"Gold: {out}")
    return out


def run_gold(spark: SparkSession, layout: MedallionLayout | None = None) -> DataFrame:
    layout = layout or default_layout()
    silver = spark.read.parquet(layout.silver("transactions"))
    gold = to_gold_features(silver)
    write_gold(gold, layout)
    return gold
