"""SparkSession compartilhada pelos jobs Medallion."""

from __future__ import annotations

import os

from pyspark.sql import SparkSession


def build_spark(app_name: str, master: str | None = None) -> SparkSession:
    master_url = master or os.environ.get("SPARK_MASTER_URL", "local[*]")
    return (
        SparkSession.builder.appName(app_name)
        .master(master_url)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .getOrCreate()
    )
