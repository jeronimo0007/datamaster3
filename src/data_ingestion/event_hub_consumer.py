"""Compat: use UnifiedKafkaConsumer — streaming do projeto é Kafka."""

from src.data_ingestion.kafka_client import UnifiedKafkaConsumer as EventHubConsumer

__all__ = ["EventHubConsumer"]
