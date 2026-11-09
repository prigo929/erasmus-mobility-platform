package ro.uaic.feaa.erasmus.agreement.domain;

import java.time.Instant;
import java.util.List;
import java.util.UUID;
import ro.uaic.feaa.erasmus.agreement.infrastructure.OutboxMessage;

public interface IOutboxRepository {
    void save(OutboxMessage message);
    List<OutboxMessage> findPendingMessages(int limit);
    void markAsPublished(UUID id, Instant at);
}
