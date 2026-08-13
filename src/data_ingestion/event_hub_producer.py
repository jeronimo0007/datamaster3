"""Compat: use UnifiedKafkaProducer — streaming do projeto é Kafka."""

from src.data_ingestion.kafka_client import UnifiedKafkaProducer as EventHubProducer

__all__ = ["EventHubProducer"]
