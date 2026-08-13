"""
Camada Silver — dados limpos, tipados e harmonizados.

Na arquitetura Medallion de referência (Databricks/Delta), a Silver é a camada
de **harmonização**: unifica múltiplas fontes num schema canônico, aplica
regras de negócio, deduplicação e enriquecimento, e só entra após o DQ gate.

Responsabilidades:
- deduplicação por `transaction_id`;
- tipagem consistente (amount, timestamps);
- regras de domínio (amount não-negativo, categorias conhecidas);
- features derivadas (is_weekend, is_night, mês);
- agregações por usuário/merchant (enriquecimento).
"""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    count,
    dayofweek,
    hour,
    month,
    stddev,
    to_date,
    when,
)

from src.data_architecture.medallion import MedallionLayout, default_layout


def clean(df: DataFrame) -> DataFrame:
    return (
        df.dropDuplicates(["transaction_id"])
        .fillna({"amount": 0, "merchant_category": "UNKNOWN", "user_country": "UNKNOWN"})
        .withColumn("amount", when(col("amount") < 0, 0).otherwise(col("amount")))
        .withColumn("transaction_date", to_date(col("timestamp")))
        .withColumn("transaction_hour", hour(col("timestamp")))
    )


def enrich(df: DataFrame) -> DataFrame:
    df = (
        df.withColumn(
            "is_weekend",
            when(dayofweek(col("transaction_date")).isin([1, 7]), 1).otherwise(0),
        )
        .withColumn(
            "is_night",
            when((col("transaction_hour") >= 0) & (col("transaction_hour") < 6), 1).otherwise(0),
        )
        .withColumn("transaction_month", month(col("transaction_date")))
    )
    user_stats = df.groupBy("user_id").agg(
        avg("amount").alias("user_avg_amount"),
        count("*").alias("user_total_transactions"),
        stddev("amount").alias("user_amount_stddev"),
    )
    df = df.join(user_stats, "user_id", "left")
    if "merchant_id" in df.columns:
        merchant_stats = df.groupBy("merchant_id").agg(
            count("*").alias("merchant_transaction_count"),
            avg("amount").alias("merchant_avg_amount"),
        )
        df = df.join(merchant_stats, "merchant_id", "left")
    return df


def write_silver(df: DataFrame, layout: MedallionLayout | None = None) -> str:
    layout = layout or default_layout()
    out = layout.silver("transactions")
    df.write.mode("overwrite").partitionBy("transaction_date").parquet(out)
    print(f"Silver: {out}")
    return out


def run_silver(spark: SparkSession, layout: MedallionLayout | None = None) -> DataFrame:
    layout = layout or default_layout()
    bronze = spark.read.parquet(layout.bronze("transactions"))
    enriched = enrich(clean(bronze))
    write_silver(enriched, layout)
    return enriched
