#!/usr/bin/env python3
"""
Ingestão multi-formato para a zona landing.

Gera/baixa dados de fraude e materializa 4 formatos:
  JSON, CSV, Parquet, XML

Fontes:
  - Gerador sintético local (sempre disponível)
  - Dataset público Credit Card Fraud (OpenML / CSV remoto) quando houver rede
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_ingestion.landing_writer import write_multi_format_landing
from src.data_ingestion.public_fraud_sources import collect_fraud_records


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingestão multi-formato → landing")
    parser.add_argument("-n", "--n-synthetic", type=int, default=400)
    parser.add_argument("--skip-public", action="store_true")
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    records = collect_fraud_records(
        n_synthetic=args.n_synthetic,
        fetch_public=not args.skip_public,
    )
    paths = write_multi_format_landing(records, run_id=args.run_id)
    print("Landing escrita:")
    for fmt, path in paths.items():
        print(f"  {fmt}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
