"""
Cliente Kafka — o mesmo no Docker local, Azure e AWS.

Configure só o bootstrap (e auth se a nuvem exigir TLS/SASL):

  KAFKA_BOOTSTRAP_SERVERS=kafka:29092          # local compose
  KAFKA_BOOTSTRAP_SERVERS=<broker>:9092        # Azure / AWS (Kafka)

Não substituir por Event Hubs, Kinesis ou outro produto na narrativa:
o componente de streaming do projeto é Kafka.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Iterable

logger = logging.getLogger(__name__)


def kafka_producer_config() -> dict[str, Any]:
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    cfg: dict[str, Any] = {
        "bootstrap.servers": bootstrap,
        "client.id": os.environ.get("KAFKA_CLIENT_ID", "datamaster-producer"),
    }
    protocol = os.environ.get("KAFKA_SECURITY_PROTOCOL")
    if protocol:
        cfg["security.protocol"] = protocol
        cfg["sasl.mechanism"] = os.environ.get("KAFKA_SASL_MECHANISM", "PLAIN")
        cfg["sasl.username"] = os.environ.get("KAFKA_SASL_USERNAME", "")
        cfg["sasl.password"] = os.environ.get("KAFKA_SASL_PASSWORD", "")
    return cfg


def kafka_consumer_config(group_id: str | None = None) -> dict[str, Any]:
    cfg = kafka_producer_config()
    cfg["group.id"] = group_id or os.environ.get("KAFKA_GROUP_ID", "datamaster-consumers")
    cfg["auto.offset.reset"] = os.environ.get("KAFKA_AUTO_OFFSET_RESET", "earliest")
    return cfg


class UnifiedKafkaProducer:
    def __init__(self, topic: str | None = None):
        self.topic = topic or os.environ.get("FRAUD_KAFKA_TOPIC", "transaction-analyzed")
        self._producer = None

    def _ensure(self):
        if self._producer is not None:
            return
        try:
            from confluent_kafka import Producer
        except ImportError as exc:
            raise ImportError(
                "Instale confluent-kafka para publicar eventos. "
                "Na API Java o cliente Spring Kafka cobre o serving."
            ) from exc
        self._producer = Producer(kafka_producer_config())

    def send(self, payload: dict[str, Any], key: str | None = None) -> None:
        self._ensure()
        assert self._producer is not None
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._producer.produce(self.topic, value=data, key=(key or "").encode("utf-8") or None)
        self._producer.poll(0)

    def send_batch(self, payloads: Iterable[dict[str, Any]]) -> int:
        n = 0
        for item in payloads:
            key = str(item.get("transaction_id") or "")
            self.send(item, key=key)
            n += 1
        self.flush()
        return n

    def flush(self, timeout: float = 10.0) -> None:
        if self._producer is not None:
            self._producer.flush(timeout)


class UnifiedKafkaConsumer:
    def __init__(self, topic: str | None = None, group_id: str | None = None):
        self.topic = topic or os.environ.get("FRAUD_KAFKA_TOPIC", "transaction-analyzed")
        self.group_id = group_id
        self._consumer = None

    def _ensure(self):
        if self._consumer is not None:
            return
        from confluent_kafka import Consumer

        self._consumer = Consumer(kafka_consumer_config(self.group_id))
        self._consumer.subscribe([self.topic])

    def poll_json(self, timeout: float = 1.0) -> dict[str, Any] | None:
        self._ensure()
        assert self._consumer is not None
        msg = self._consumer.poll(timeout)
        if msg is None or msg.error():
            return None
        return json.loads(msg.value().decode("utf-8"))

    def close(self) -> None:
        if self._consumer is not None:
            self._consumer.close()
            self._consumer = None
