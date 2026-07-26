package com.fraud.local.mongo;

import java.time.Instant;
import java.util.List;
import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

/** Espelho consultável dos eventos publicados no Kafka (Jupyter / API). */
@Data
@Document(collection = "analyzed_events")
public class AnalyzedEventDocument {

    @Id
    private String id;

    @Indexed
    @Field("event_id")
    private String eventId;

    @Field("event_type")
    private String eventType;

    @Field("event_version")
    private Integer eventVersion;

    @Indexed
    @Field("occurred_at")
    private Instant occurredAt;

    /** yyyy-MM-dd UTC — filtro rápido “do dia”. */
    @Indexed
    @Field("event_day")
    private String eventDay;

    @Indexed
    @Field("transaction_id")
    private String transactionId;

    @Field("user_id")
    private String userId;

    private String cpf;

    @Field("card_last4")
    private String cardLast4;

    private Double amount;

    @Field("merchant_category")
    private String merchantCategory;

    @Field("payment_method")
    private String paymentMethod;

    @Field("fraud_score")
    private Double fraudScore;

    @Field("is_fraud")
    private Boolean isFraud;

    @Field("risk_level")
    private String riskLevel;

    @Field("recommended_action")
    private String recommendedAction;

    @Field("anomaly_reasons")
    private List<String> anomalyReasons;

    @Field("processing_time_ms")
    private Double processingTimeMs;

    @Field("kafka_topic")
    private String kafkaTopic;

    @Field("kafka_published")
    private Boolean kafkaPublished;
}
