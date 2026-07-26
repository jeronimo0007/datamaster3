package com.fraud.messaging;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Profile;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

/**
 * Publica {@link TransactionAnalyzedEvent} no Kafka de forma assíncrona.
 * Falha no broker não quebra a resposta HTTP do {@code /analyze}.
 */
@Service
@Profile("local")
@ConditionalOnProperty(name = "fraud.kafka.enabled", havingValue = "true", matchIfMissing = true)
@RequiredArgsConstructor
@Slf4j
public class TransactionAnalyzedEventPublisher {

    private final KafkaTemplate<String, TransactionAnalyzedEvent> kafkaTemplate;

    @Value("${fraud.kafka.topic:transaction-analyzed}")
    private String topic;

    @Async("kafkaEventExecutor")
    public void publishAsync(TransactionAnalyzedEvent event) {
        if (event == null || event.getTransactionId() == null) {
            return;
        }
        try {
            kafkaTemplate
                    .send(topic, event.getTransactionId(), event)
                    .whenComplete(
                            (result, ex) -> {
                                if (ex != null) {
                                    log.warn(
                                            "Falha ao publicar no Kafka (API já respondeu): tx={} — {}",
                                            event.getTransactionId(),
                                            ex.getMessage());
                                } else {
                                    log.info(
                                            "Evento transaction-analyzed publicado: tx={} partition={}",
                                            event.getTransactionId(),
                                            result.getRecordMetadata().partition());
                                }
                            });
        } catch (Exception e) {
            log.warn(
                    "Erro ao enfileirar publicação Kafka: tx={} — {}",
                    event.getTransactionId(),
                    e.getMessage());
        }
    }
}
