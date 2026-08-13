"""Transformações Medallion — import lazy para não exigir PySpark no Airflow."""

from .dq import assert_dq_gate, run_dq_checks, write_dq_report

__all__ = [
    "assert_dq_gate",
    "run_dq_checks",
    "write_dq_report",
    "build_spark",
    "run_bronze",
    "run_silver",
    "run_gold",
]


def __getattr__(name: str):
    if name == "build_spark":
        from .spark_session import build_spark

        return build_spark
    if name == "run_bronze":
        from .bronze import run_bronze

        return run_bronze
    if name == "run_silver":
        from .silver import run_silver

        return run_silver
    if name == "run_gold":
        from .gold import run_gold

        return run_gold
    raise AttributeError(name)
