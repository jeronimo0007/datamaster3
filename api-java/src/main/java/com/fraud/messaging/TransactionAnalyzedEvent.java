package com.fraud.messaging;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import java.util.List;
import lombok.Builder;
import lombok.Data;

/**
 * Evento publicado no Kafka após {@code POST /analyze}.
 * Contém CPF e apenas os 4 últimos dígitos do cartão (não o PAN completo).
 */
@Data
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TransactionAnalyzedEvent {

    @JsonProperty("event_id")
    private String eventId;

    @JsonProperty("event_type")
    private String eventType;

    @JsonProperty("event_version")
    private int eventVersion;

    @JsonProperty("occurred_at")
    private Instant occurredAt;

    @JsonProperty("transaction_id")
    private String transactionId;

    @JsonProperty("user_id")
    private String userId;

    /** CPF / documento do portador (demo). */
    private String cpf;

    /** Apenas os 4 últimos dígitos do cartão. */
    @JsonProperty("card_last4")
    private String cardLast4;

    private Double amount;

    @JsonProperty("merchant_category")
    private String merchantCategory;

    @JsonProperty("payment_method")
    private String paymentMethod;

    @JsonProperty("fraud_score")
    private Double fraudScore;

    @JsonProperty("is_fraud")
    private Boolean isFraud;

    @JsonProperty("risk_level")
    private String riskLevel;

    @JsonProperty("recommended_action")
    private String recommendedAction;

    @JsonProperty("anomaly_reasons")
    private List<String> anomalyReasons;

    @JsonProperty("processing_time_ms")
    private Double processingTimeMs;

    @JsonProperty("event_day")
    private String eventDay;
}
