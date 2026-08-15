"""
Arquitetura Medallion (Bronze / Silver / Gold).

Camadas
-------
- **Bronze:** landing fiel à origem (schema flexível, retenção maior, auditoria).
- **Silver:** harmonização — dados limpos, deduplicados, tipados; regras de
  negócio, schema canônico e DQ. É a camada que unifica fontes heterogêneas.
- **Gold:** agregados e datasets de consumo (BI, ML serving batch, feature sets).

O mesmo layout de prefixos funciona em **ADLS Gen2** (Azure) ou filesystem local,
por exemplo: `abfss://bronze@storage.dfs.core.windows.net/transactions`
ou `file:///.../data/lake/bronze/transactions`.

Streaming complementar
----------------------
Kafka no Docker local, Azure e AWS publicam eventos de
negócio analisados. O lake Medallion é orquestrado pelo Airflow (jobs por camada).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Layer = Literal["bronze", "silver", "gold", "landing"]


@dataclass(frozen=True)
class MedallionLayout:
    """
    Prefixos padrão no lake — única fonte de paths para código, Airflow e docs.

    base_uri exemplos:
    - Azure: abfss://container@storage.dfs.core.windows.net/fraud
    - Local demo: file:///.../data/lake
    """

    base_uri: str

    def path(self, layer: Layer, entity: str = "transactions") -> str:
        key = str(layer).lower()
        return f"{self.base_uri.rstrip('/')}/{key}/{entity.strip('/')}"

    def bronze(self, entity: str = "transactions") -> str:
        return self.path("bronze", entity)

    def silver(self, entity: str = "transactions") -> str:
        return self.path("silver", entity)

    def gold(self, entity: str = "transactions_ml") -> str:
        return self.path("gold", entity)

    def reports(self) -> str:
        return f"{self.base_uri.rstrip('/')}/reports"


def project_root() -> Path:
    return Path(os.environ.get("PROJECT_ROOT", Path(__file__).resolve().parents[2]))


def default_layout(root: Path | None = None) -> MedallionLayout:
    """
    Layout padrão do lake.

    - Se `LAKE_BASE_URI` estiver definido (ADLS / S3 / outro),
      usa essa URI como base
      (ex.: `abfss://lake@account.dfs.core.windows.net` ou `s3://bucket`).
    - Senão, usa `data/lake` local.
    """
    remote = os.environ.get("LAKE_BASE_URI", "").strip()
    if remote:
        if remote.startswith("file://"):
            return MedallionLayout(base_uri=Path(remote.replace("file://", "")).as_uri())
        return MedallionLayout(base_uri=remote.rstrip("/"))
    base = root or project_root()
    lake = base / "data" / "lake"
    lake.mkdir(parents=True, exist_ok=True)
    return MedallionLayout(base_uri=lake.as_uri())


def landing_dir(root: Path | None = None) -> Path | str:
    """
    Raiz da zona landing.

    - Se `LANDING_BASE_URI` estiver definido, retorna a URI remota
      (ex.: `abfss://.../landing` ou `s3://bucket/landing`).
    - Se começar com `file://`, converte para Path local.
    - Senão, usa `data/landing` local.
    """
    remote = os.environ.get("LANDING_BASE_URI", "").strip()
    if remote:
        if remote.startswith("file://"):
            path = Path(remote.replace("file://", ""))
            path.mkdir(parents=True, exist_ok=True)
            return path
        return remote.rstrip("/")
    base = root or project_root()
    path = base / "data" / "landing"
    path.mkdir(parents=True, exist_ok=True)
    return path


# Aliases históricos (notebook legado raw/processed/curated)
LAYER_ALIASES: dict[str, Layer] = {
    "raw": "bronze",
    "landing": "landing",
    "processed": "silver",
    "curated": "gold",
}
