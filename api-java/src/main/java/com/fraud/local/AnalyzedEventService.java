package com.fraud.local;

import com.fraud.local.mongo.AnalyzedEventDocument;
import com.fraud.local.mongo.AnalyzedEventRepository;
import com.fraud.messaging.FraudKafkaConstants;
import com.fraud.messaging.TransactionAnalyzedEvent;
import com.fraud.messaging.TransactionAnalyzedEventPublisher;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Service;

/**
 * Monta o evento (CPF + card_last4), persiste para consulta (Jupyter/API)
 * e dispara publicação assíncrona no Kafka.
 */
@Service
@Profile("local")
public class AnalyzedEventService {

    private final AnalyzedEventRepository repository;

    @Autowired(required = false)
    private TransactionAnalyzedEventPublisher kafkaPublisher;

    public AnalyzedEventService(AnalyzedEventRepository repository) {
        this.repository = repository;
    }

    public TransactionAnalyzedEvent publishFromAnalyzeRecord(Map<String, Object> record) {
        Instant occurredAt = parseInstant(record.get("timestamp"));
        String eventDay = LocalDate.ofInstant(occurredAt, ZoneOffset.UTC).toString();
        String cpf = stringVal(record.get("holder_document"));
        String cardLast4 = last4(stringVal(record.get("card_number")));

        TransactionAnalyzedEvent event =
                TransactionAnalyzedEvent.builder()
                        .eventId(UUID.randomUUID().toString())
                        .eventType("transaction.analyzed")
                        .eventVersion(1)
                        .occurredAt(occurredAt)
                        .transactionId(stringVal(record.get("transaction_id")))
                        .userId(stringVal(record.get("profile_user_id")))
                        .cpf(cpf)
                        .cardLast4(cardLast4)
                        .amount(num(record.get("amount")))
                        .merchantCategory(stringVal(record.get("merchant_category")))
                        .paymentMethod(stringVal(record.get("payment_method")))
                        .fraudScore(num(record.get("fraud_score")))
                        .isFraud(bool(record.get("is_fraud")))
                        .riskLevel(stringVal(record.get("risk_level")))
                        .recommendedAction(stringVal(record.get("recommended_action")))
                        .anomalyReasons(stringList(record.get("anomaly_reasons")))
                        .processingTimeMs(num(record.get("processing_time_ms")))
                        .eventDay(eventDay)
                        .build();

        AnalyzedEventDocument doc = toDocument(event);
        doc.setKafkaTopic(FraudKafkaConstants.TOPIC_TRANSACTION_ANALYZED);
        doc.setKafkaPublished(kafkaPublisher != null);
        repository.save(doc);

        if (kafkaPublisher != null) {
            kafkaPublisher.publishAsync(event);
        }
        return event;
    }

    public Map<String, Object> listByDay(String day) {
        String eventDay = resolveDay(day);
        List<AnalyzedEventDocument> docs = repository.findByEventDayOrderByOccurredAtDesc(eventDay);
        List<Map<String, Object>> items = new ArrayList<>();
        for (AnalyzedEventDocument d : docs) {
            items.add(toMap(d));
        }
        long frauds = repository.countByEventDayAndIsFraudTrue(eventDay);
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("event_day", eventDay);
        out.put("total", items.size());
        out.put("frauds", frauds);
        out.put("legit", items.size() - frauds);
        out.put("kafka_topic", FraudKafkaConstants.TOPIC_TRANSACTION_ANALYZED);
        out.put("events", items);
        return out;
    }

    public static String last4(String cardNumber) {
        if (cardNumber == null) {
            return "";
        }
        String digits = cardNumber.replaceAll("\\D", "");
        if (digits.length() <= 4) {
            return digits;
        }
        return digits.substring(digits.length() - 4);
    }

    private static String resolveDay(String day) {
        if (day == null || day.isBlank() || "today".equalsIgnoreCase(day) || "hoje".equalsIgnoreCase(day)) {
            return LocalDate.now(ZoneOffset.UTC).toString();
        }
        return day.trim();
    }

    private static AnalyzedEventDocument toDocument(TransactionAnalyzedEvent e) {
        AnalyzedEventDocument d = new AnalyzedEventDocument();
        d.setEventId(e.getEventId());
        d.setEventType(e.getEventType());
        d.setEventVersion(e.getEventVersion());
        d.setOccurredAt(e.getOccurredAt());
        d.setEventDay(e.getEventDay());
        d.setTransactionId(e.getTransactionId());
        d.setUserId(e.getUserId());
        d.setCpf(e.getCpf());
        d.setCardLast4(e.getCardLast4());
        d.setAmount(e.getAmount());
        d.setMerchantCategory(e.getMerchantCategory());
        d.setPaymentMethod(e.getPaymentMethod());
        d.setFraudScore(e.getFraudScore());
        d.setIsFraud(e.getIsFraud());
        d.setRiskLevel(e.getRiskLevel());
        d.setRecommendedAction(e.getRecommendedAction());
        d.setAnomalyReasons(e.getAnomalyReasons());
        d.setProcessingTimeMs(e.getProcessingTimeMs());
        return d;
    }

    private static Map<String, Object> toMap(AnalyzedEventDocument d) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("event_id", d.getEventId());
        m.put("event_type", d.getEventType());
        m.put("occurred_at", d.getOccurredAt() != null ? d.getOccurredAt().toString() : null);
        m.put("event_day", d.getEventDay());
        m.put("transaction_id", d.getTransactionId());
        m.put("user_id", d.getUserId());
        m.put("cpf", d.getCpf());
        m.put("card_last4", d.getCardLast4());
        m.put("amount", d.getAmount());
        m.put("merchant_category", d.getMerchantCategory());
        m.put("payment_method", d.getPaymentMethod());
        m.put("fraud_score", d.getFraudScore());
        m.put("is_fraud", d.getIsFraud());
        m.put("risk_level", d.getRiskLevel());
        m.put("recommended_action", d.getRecommendedAction());
        m.put("anomaly_reasons", d.getAnomalyReasons());
        m.put("processing_time_ms", d.getProcessingTimeMs());
        m.put("kafka_topic", d.getKafkaTopic());
        m.put("kafka_published", d.getKafkaPublished());
        return m;
    }

    private static Instant parseInstant(Object ts) {
        if (ts == null) {
            return Instant.now();
        }
        try {
            return Instant.parse(String.valueOf(ts));
        } catch (Exception e) {
            return Instant.now();
        }
    }

    private static String stringVal(Object o) {
        return o == null ? "" : String.valueOf(o);
    }

    private static Double num(Object o) {
        if (o instanceof Number n) {
            return n.doubleValue();
        }
        return null;
    }

    private static Boolean bool(Object o) {
        if (o instanceof Boolean b) {
            return b;
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    private static List<String> stringList(Object o) {
        if (o instanceof List<?> list) {
            List<String> out = new ArrayList<>();
            for (Object item : list) {
                if (item != null) {
                    out.add(String.valueOf(item));
                }
            }
            return out;
        }
        return List.of();
    }
}
