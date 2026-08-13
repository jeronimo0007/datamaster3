"""Ingestão: multi-formato, fontes públicas, Kafka unificado."""

from .kafka_client import UnifiedKafkaConsumer, UnifiedKafkaProducer
from .landing_writer import write_multi_format_landing
from .public_fraud_sources import collect_fraud_records

__all__ = [
    "UnifiedKafkaProducer",
    "UnifiedKafkaConsumer",
    "write_multi_format_landing",
    "collect_fraud_records",
]
