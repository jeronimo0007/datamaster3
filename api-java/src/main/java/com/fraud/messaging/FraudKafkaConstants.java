package com.fraud.messaging;

/** Contrato Kafka — evento após análise online (log assíncrono para consumidores). */
public final class FraudKafkaConstants {

    public static final String TOPIC_TRANSACTION_ANALYZED = "transaction-analyzed";

    private FraudKafkaConstants() {}
}
