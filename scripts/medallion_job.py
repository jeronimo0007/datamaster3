#!/usr/bin/env python3
"""
CLI por camada Medallion — Airflow e linha de comando.

Tenta PySpark; se indisponível (worker Airflow), usa pandas (mesmo contrato de paths).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run_spark(layer: str, master: str | None) -> int:
    from src.data_architecture.medallion import default_layout
    from src.data_processing import (
        assert_dq_gate,
        build_spark,
        run_bronze,
        run_dq_checks,
        run_gold,
        run_silver,
        write_dq_report,
    )

    spark = build_spark(f"medallion-{layer}", master=master)
    layout = default_layout()
    try:
        if layer in ("bronze", "all"):
            print("=== Bronze (Spark) ===")
            run_bronze(spark, layout)
        if layer in ("dq", "all"):
            print("=== DQ gate ===")
            bronze_df = spark.read.parquet(layout.bronze("transactions"))
            dq = run_dq_checks(bronze_df)
            print(json.dumps(dq, indent=2, ensure_ascii=False))
            write_dq_report(dq, layout)
            assert_dq_gate(dq)
        if layer in ("silver", "all"):
            print("=== Silver (Spark) ===")
            run_silver(spark, layout)
        if layer in ("gold", "all"):
            print("=== Gold (Spark) ===")
            run_gold(spark, layout)
        print("=== OK ===")
        return 0
    finally:
        spark.stop()


def _run_pandas(layer: str) -> int:
    from src.data_processing.pandas_pipeline import run_layer_pandas

    run_layer_pandas(layer)
    print("=== OK (pandas backend) ===")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Job Medallion por camada")
    parser.add_argument("layer", choices=["bronze", "dq", "silver", "gold", "all"])
    parser.add_argument("--master", default=None)
    parser.add_argument(
        "--backend",
        choices=["auto", "spark", "pandas"],
        default="auto",
        help="auto: Spark se disponível, senão pandas",
    )
    args = parser.parse_args()

    use_spark = args.backend == "spark"
    if args.backend == "auto":
        try:
            import pyspark  # noqa: F401

            use_spark = True
        except ImportError:
            use_spark = False
            print("PySpark indisponível — usando backend pandas")

    if use_spark:
        try:
            return _run_spark(args.layer, args.master)
        except Exception as exc:
            if args.backend == "spark":
                raise
            print(f"Spark falhou ({exc}); fallback pandas")
            return _run_pandas(args.layer)
    return _run_pandas(args.layer)


if __name__ == "__main__":
    raise SystemExit(main())
