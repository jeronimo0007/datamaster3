#!/usr/bin/env python3
"""Consulta do dia — eventos transaction-analyzed (espelho Kafka via API).

Uso no Jupyter ou no host:
  python notebooks/02_kafka_consultas_dia.py
  python notebooks/02_kafka_consultas_dia.py --day 2026-07-26
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import pandas as pd
import requests

try:
    import matplotlib.pyplot as plt
except ImportError:  # host sem matplotlib — use o Jupyter fraud-jupyter
    plt = None

API_BASES = ["http://api:8080", "http://localhost:8080"]


def fetch_day(day: str) -> dict[str, Any]:
    last_err: Exception | None = None
    for base in API_BASES:
        try:
            r = requests.get(
                f"{base}/api/v1/events/analyzed",
                params={"date": day},
                timeout=8,
            )
            r.raise_for_status()
            print(f"OK via {base}")
            return r.json()
        except Exception as e:  # noqa: BLE001
            last_err = e
    raise RuntimeError(f"Não foi possível consultar a API: {last_err}")


def plot_day(payload: dict[str, Any], df: pd.DataFrame) -> None:
    if df.empty:
        print("Nada para plotar.")
        return
    if plt is None:
        print("matplotlib não instalado neste Python — abra o notebook no Jupyter :8888")
        print("  http://localhost:8888/?token=datamaster → notebooks/02_kafka_consultas_dia.ipynb")
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fraud_counts = df["is_fraud"].fillna(False).astype(bool).value_counts()
    labels = ["Fraude" if v else "Legítimo" for v in fraud_counts.index]
    axes[0].pie(
        fraud_counts.values,
        labels=labels,
        autopct="%1.1f%%",
        colors=["#ef4444", "#22c55e"],
        startangle=90,
    )
    axes[0].set_title(f"Fraude × Legítimo — {payload.get('event_day')}")

    scores = pd.to_numeric(df["fraud_score"], errors="coerce").dropna()
    axes[1].hist(scores, bins=12, color="#38bdf8", edgecolor="white")
    axes[1].axvline(0.74, color="#f59e0b", linestyle="--", label="limiar 0,74")
    axes[1].set_title("Distribuição de fraud_score")
    axes[1].set_xlabel("score")
    axes[1].set_ylabel("qtd")
    axes[1].legend()
    plt.tight_layout()
    out = "data/events/analyzed_hoje.png"
    try:
        from pathlib import Path

        Path("data/events").mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=120, bbox_inches="tight")
        print(f"Gráfico salvo em {out}")
    except Exception as e:  # noqa: BLE001
        print(f"Não salvei PNG ({e}); exibindo se houver backend gráfico.")
    plt.show()


def main() -> int:
    parser = argparse.ArgumentParser(description="Consulta eventos Kafka do dia")
    parser.add_argument("--day", default="today", help="today|hoje|YYYY-MM-DD")
    args = parser.parse_args()

    payload = fetch_day(args.day)
    summary = {k: payload[k] for k in ("event_day", "total", "frauds", "legit", "kafka_topic")}
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    events = payload.get("events") or []
    df = pd.DataFrame(events)
    if df.empty:
        print("Sem eventos. Rode alguns POST /analyze e tente de novo.")
        return 0

    cols = [
        c
        for c in [
            "occurred_at",
            "transaction_id",
            "cpf",
            "card_last4",
            "amount",
            "fraud_score",
            "is_fraud",
            "risk_level",
            "merchant_category",
        ]
        if c in df.columns
    ]
    print(df[cols].to_string(index=False))
    plot_day(payload, df)
    return 0


if __name__ == "__main__":
    sys.exit(main())
