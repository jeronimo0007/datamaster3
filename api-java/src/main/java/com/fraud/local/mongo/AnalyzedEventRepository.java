package com.fraud.local.mongo;

import java.util.List;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface AnalyzedEventRepository extends MongoRepository<AnalyzedEventDocument, String> {

    List<AnalyzedEventDocument> findByEventDayOrderByOccurredAtDesc(String eventDay);

    long countByEventDay(String eventDay);

    long countByEventDayAndIsFraudTrue(String eventDay);
}
