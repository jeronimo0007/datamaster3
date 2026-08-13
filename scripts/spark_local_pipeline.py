#!/usr/bin/env python3
"""
Pipeline Medallion (compat): delega para scripts/medallion_job.py all.

Preferir camadas via Airflow (medallion_pipeline) ou:
  python3 scripts/medallion_job.py bronze|dq|silver|gold|all
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    # preserva CLI antiga: spark_local_pipeline.py [-i ...] --master ...
    # mapeia para job all
    sys.argv = [str(Path(__file__).with_name("medallion_job.py")), "all"] + [
        a for a in sys.argv[1:] if a in ("--master",) or not a.startswith("-")
    ]
    # simplifica: sempre all
    sys.argv = [sys.argv[0], "all"]
    runpy.run_path(str(Path(__file__).with_name("medallion_job.py")), run_name="__main__")
