"""
Coleta de dados de fraude: sintético + fonte pública.

Fonte pública: amostra do dataset Credit Card Fraud (OpenML id 1597)
via CSV remoto — demonstra ingestão HTTP real sem credenciais.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

logger = logging.getLogger(__name__)

# Amostra pequena hospedada (OpenML / raw gist-style CSV público)
PUBLIC_FRAUD_CSV_URLS = [
    # OpenML credit-card-fraud sample mirror (primeiras linhas suficientes para demo)
    "https://raw.githubusercontent.com/nsethi31/Kaggle-Data-Credit-Card-Fraud-Detection/master/creditcard.csv",
]

MERCHANT_CATEGORIES = [
    "Eletronicos",
    "Alimentacao",
    "Vestuario",
    "Servicos",
    "Viagem",
    "Entretenimento",
]
PAYMENT_METHODS = ["CREDIT_CARD", "DEBIT_CARD", "PIX", "BOLETO"]
COUNTRIES = ["BR", "US", "AR", "PT", "MX"]


def _synthetic_record(i: int, base_time: datetime) -> dict[str, Any]:
    is_fraud = random.random() < 0.08
    amount = round(random.uniform(5, 8000) * (3 if is_fraud else 1), 2)
    ts = base_time - timedelta(minutes=random.randint(0, 60 * 24 * 14))
    user_country = random.choice(COUNTRIES)
    merchant_country = random.choice(COUNTRIES) if is_fraud and random.random() < 0.4 else user_country
    return {
        "transaction_id": f"syn-{uuid.uuid4().hex[:12]}",
        "user_id": f"user_{random.randint(1, 120):04d}",
        "merchant_id": f"mrc_{random.randint(1, 40):03d}",
        "amount": amount,
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "payment_method": random.choice(PAYMENT_METHODS),
        "user_country": user_country,
        "merchant_country": merchant_country,
        "timestamp": ts.isoformat(timespec="seconds"),
        "is_fraud": is_fraud,
        "source": "synthetic",
    }


def generate_synthetic(n: int = 400) -> list[dict[str, Any]]:
    random.seed(42)
    base = datetime.utcnow()
    return [_synthetic_record(i, base) for i in range(n)]


def fetch_public_creditcard_sample(max_rows: int = 200) -> list[dict[str, Any]]:
    """
    Baixa CSV público de fraude com cartão e mapeia para schema canônico.
    Colunas originais: Time, V1..V28, Amount, Class
    """
    last_err: Exception | None = None
    for url in PUBLIC_FRAUD_CSV_URLS:
        try:
            with urlopen(url, timeout=45) as resp:
                text = resp.read().decode("utf-8", errors="replace")
            reader = csv.DictReader(io.StringIO(text))
            out: list[dict[str, Any]] = []
            base = datetime.utcnow()
            for i, row in enumerate(reader):
                if i >= max_rows:
                    break
                amount = float(row.get("Amount") or 0)
                is_fraud = str(row.get("Class", "0")).strip() in ("1", "1.0")
                seconds = float(row.get("Time") or i)
                ts = base - timedelta(seconds=max(0, 172800 - seconds))
                out.append(
                    {
                        "transaction_id": f"pub-{i:06d}-{uuid.uuid4().hex[:6]}",
                        "user_id": f"user_{int(seconds) % 120:04d}",
                        "merchant_id": f"mrc_{int(amount) % 40:03d}",
                        "amount": amount,
                        "merchant_category": MERCHANT_CATEGORIES[i % len(MERCHANT_CATEGORIES)],
                        "payment_method": "CREDIT_CARD",
                        "user_country": "BR",
                        "merchant_country": "BR" if not is_fraud else "US",
                        "timestamp": ts.isoformat(timespec="seconds"),
                        "is_fraud": is_fraud,
                        "source": "public_creditcard_csv",
                    }
                )
            logger.info("Fonte pública: %s linhas de %s", len(out), url)
            return out
        except (URLError, TimeoutError, ValueError, KeyError) as exc:
            last_err = exc
            logger.warning("Falha ao baixar %s: %s", url, exc)
    if last_err:
        logger.warning("Sem rede/fonte pública — usando só sintético (%s)", last_err)
    return []


def collect_fraud_records(
    n_synthetic: int = 400,
    fetch_public: bool = True,
    public_max_rows: int = 200,
) -> list[dict[str, Any]]:
    records = generate_synthetic(n_synthetic)
    if fetch_public:
        records.extend(fetch_public_creditcard_sample(public_max_rows))
    return records
