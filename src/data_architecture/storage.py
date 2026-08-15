"""
Acesso unificado a storage: filesystem local (`file`) ou ADLS Gen2 (`abfss`).

Estratégia:
- Operações locais usam `pathlib`/`shutil` (sem dependências externas).
- URIs remotas (`abfss://`, `s3://`, ...) usam `fsspec`/`adlfs`, com import lazy
  para que o pipeline local nunca exija essas libs instaladas.

Protocolo é inferido pela URI (`abfss://`, `s3://`, ...). Sem protocolo = local.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

# Prefixos configuráveis por ambiente (Azure/AWS sobrescrevem via env vars)
LAKE_BASE = os.environ.get("LAKE_BASE_URI", "")
LANDING_BASE = os.environ.get("LANDING_BASE_URI", "")

REMOTE_SCHEMES = ("abfss://", "abfs://", "s3://", "gs://")


def is_remote(path: Any) -> bool:
    uri = str(path)
    # file:// (produzido por Path.as_uri) continua sendo local
    return uri.startswith(REMOTE_SCHEMES) or (
        "://" in uri and not uri.startswith("file://")
    )


def _fs_split(path: Any) -> tuple[Any, str]:
    import fsspec

    uri = str(path)
    proto, _ = fsspec.core.split_protocol(uri)
    if proto:
        return fsspec.filesystem(proto), uri
    fs = fsspec.filesystem("file")
    return fs, uri


def join(base: str, *parts: str) -> str:
    out = base.rstrip("/")
    for part in parts:
        out = out + "/" + part.strip("/")
    return out


def to_local_path(path: Any) -> Path:
    """Converte URI `file://` (ou path comum) em Path local."""
    uri = str(path)
    if uri.startswith("file://"):
        return Path(uri.replace("file://", ""))
    return Path(uri)


def exists(path: Any) -> bool:
    if is_remote(path):
        fs, p = _fs_split(path)
        return fs.exists(p)
    return Path(path).exists()


def isdir(path: Any) -> bool:
    if is_remote(path):
        fs, p = _fs_split(path)
        return fs.isdir(p)
    return Path(path).is_dir()


def makedirs(path: Any, exist_ok: bool = True) -> None:
    if is_remote(path):
        fs, p = _fs_split(path)
        fs.makedirs(p, exist_ok=exist_ok)
    else:
        Path(path).mkdir(parents=True, exist_ok=exist_ok)


def rmtree(path: Any) -> None:
    if is_remote(path):
        fs, p = _fs_split(path)
        if fs.exists(p):
            fs.rm(p, recursive=True)
    else:
        p = Path(path)
        if p.exists():
            shutil.rmtree(p)


def write_text(path: Any, content: str, encoding: str = "utf-8") -> None:
    if is_remote(path):
        fs, p = _fs_split(path)
        with fs.open(p, "wt", encoding=encoding) as f:
            f.write(content)
    else:
        Path(path).write_text(content, encoding=encoding)


def read_text(path: Any, encoding: str = "utf-8") -> str:
    if is_remote(path):
        fs, p = _fs_split(path)
        with fs.open(p, "rt", encoding=encoding) as f:
            return f.read()
    return Path(path).read_text(encoding=encoding)


def write_bytes(path: Any, content: bytes) -> None:
    if is_remote(path):
        fs, p = _fs_split(path)
        with fs.open(p, "wb") as f:
            f.write(content)
    else:
        Path(path).write_bytes(content)


def read_bytes(path: Any) -> bytes:
    if is_remote(path):
        fs, p = _fs_split(path)
        with fs.open(p, "rb") as f:
            return f.read()
    return Path(path).read_bytes()


def glob(pattern: str) -> list[str]:
    """Glob recursivo; devolve lista ordenada desc (mais recente primeiro)."""
    if is_remote(pattern):
        import fsspec

        base = pattern.split("*", 1)[0]
        fs, _ = _fs_split(base)
        found = fs.glob(pattern)
        return sorted(found, reverse=True)
    from glob import glob as _glob

    return sorted(_glob(pattern, recursive=True), reverse=True)


def list_runs(base: str) -> list[str]:
    """Lista diretórios `run=*` imediatos, ordenados desc (mais recente primeiro)."""
    if is_remote(base):
        fs, p = _fs_split(base)
        runs = [d for d in fs.glob(p.rstrip("/") + "/run=*") if fs.isdir(d)]
        return sorted(runs, reverse=True)
    p = Path(base)
    runs = [str(d) for d in p.glob("run=*") if d.is_dir()]
    return sorted(runs, reverse=True)


def write_parquet(df: Any, path: Any, **kwargs: Any) -> None:
    """df.to_parquet com suporte a URI remota (fsspec/adlfs)."""
    df.to_parquet(path, **kwargs)


def read_parquet(path: Any, **kwargs: Any) -> Any:
    import pandas as pd

    return pd.read_parquet(path, **kwargs)


def local_or_uri(base: str, rel: Path) -> str:
    """Monta path efetivo: se base é URI, junta; senão usa Path relativo ao base local."""
    uri = str(base)
    if "://" in uri:
        return join(uri, *rel.parts)
    return str(Path(uri) / rel)


def ensure_dir(path: Any) -> None:
    makedirs(path, exist_ok=True)
