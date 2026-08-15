"""Testes do acesso a storage remoto (ADLS via fsspec) sem depender da Azure.

Usa o filesystem `memory://` do fsspec para exercitar o ramo "remoto" do
módulo `src.data_architecture.storage` e o layout ADLS do Medallion.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_architecture import storage  # noqa: E402
from src.data_architecture.medallion import (  # noqa: E402
    MedallionLayout,
    default_layout,
    landing_dir,
)


class StorageRemoteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fs = storage._fs_split("memory://bucket")[0]  # noqa: SLF001
        self.fs.rm("memory://bucket", recursive=True) if self.fs.exists("memory://bucket") else None

    def test_is_remote(self) -> None:
        self.assertTrue(storage.is_remote("abfss://lake@acct.dfs.core.windows.net"))
        self.assertTrue(storage.is_remote("s3://bucket/key"))
        self.assertTrue(storage.is_remote("memory://bucket"))
        self.assertFalse(storage.is_remote("/tmp/local/path"))
        self.assertFalse(storage.is_remote("file:///tmp/local/path"))
        self.assertFalse(storage.is_remote(Path("/tmp/local/path")))

    def test_write_read_bytes_text(self) -> None:
        base = "memory://bucket/lake"
        storage.makedirs(base)
        storage.write_text(base + "/hello.txt", "olá mundo")
        self.assertEqual(storage.read_text(base + "/hello.txt"), "olá mundo")
        storage.write_bytes(base + "/bin.dat", b"\x00\x01\x02")
        self.assertEqual(storage.read_bytes(base + "/bin.dat"), b"\x00\x01\x02")

    def test_glob_and_rmtree(self) -> None:
        base = "memory://bucket/lake/bronze/transactions"
        storage.makedirs(base)
        storage.write_text(base + "/part-000.parquet", "x")
        runs = storage.list_runs("memory://bucket/lake/landing")
        self.assertEqual(runs, [])
        found = storage.glob(base + "/*.parquet")
        self.assertEqual(len(found), 1)
        storage.rmtree(base)
        self.assertFalse(storage.exists(base))

    def test_list_runs(self) -> None:
        storage.makedirs("memory://bucket/landing/run=20260814T000000Z")
        storage.makedirs("memory://bucket/landing/run=20260814T010000Z")
        runs = storage.list_runs("memory://bucket/landing")
        self.assertEqual(len(runs), 2)
        self.assertIn("20260814T010000Z", runs[0])  # mais recente primeiro

    def test_adls_layout(self) -> None:
        os.environ["LAKE_BASE_URI"] = "abfss://lake@acct.dfs.core.windows.net"
        os.environ["LANDING_BASE_URI"] = "abfss://lake@acct.dfs.core.windows.net/landing"
        try:
            layout = default_layout()
            self.assertEqual(layout.bronze("transactions"),
                             "abfss://lake@acct.dfs.core.windows.net/bronze/transactions")
            self.assertEqual(layout.silver("transactions"),
                             "abfss://lake@acct.dfs.core.windows.net/silver/transactions")
            self.assertEqual(layout.gold("transactions_ml"),
                             "abfss://lake@acct.dfs.core.windows.net/gold/transactions_ml")
            self.assertEqual(layout.reports(),
                             "abfss://lake@acct.dfs.core.windows.net/reports")
            landing = landing_dir()
            self.assertEqual(str(landing), "abfss://lake@acct.dfs.core.windows.net/landing")
        finally:
            del os.environ["LAKE_BASE_URI"]
            del os.environ["LANDING_BASE_URI"]

    def test_s3_layout(self) -> None:
        os.environ["LAKE_BASE_URI"] = "s3://datamaster-lake-demo"
        os.environ["LANDING_BASE_URI"] = "s3://datamaster-lake-demo/landing"
        try:
            layout = default_layout()
            self.assertEqual(layout.bronze("transactions"),
                             "s3://datamaster-lake-demo/bronze/transactions")
            self.assertEqual(layout.silver("transactions"),
                             "s3://datamaster-lake-demo/silver/transactions")
            self.assertEqual(layout.gold("transactions_ml"),
                             "s3://datamaster-lake-demo/gold/transactions_ml")
            self.assertEqual(layout.reports(),
                             "s3://datamaster-lake-demo/reports")
            landing = landing_dir()
            self.assertEqual(str(landing), "s3://datamaster-lake-demo/landing")
        finally:
            del os.environ["LAKE_BASE_URI"]
            del os.environ["LANDING_BASE_URI"]

    def test_manual_layout_local(self) -> None:
        layout = MedallionLayout(base_uri=Path("/data/lake").as_uri())
        self.assertTrue(layout.bronze("transactions").startswith("file://"))


if __name__ == "__main__":
    unittest.main()
