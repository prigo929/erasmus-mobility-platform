package ro.uaic.feaa.erasmus.agreement.infrastructure;

import java.util.Objects;
import java.util.UUID;
import ro.uaic.feaa.erasmus.agreement.domain.LearningAgreementHostConfirmedEvent;

public record OutboxMessage(UUID id, UUID aggregateId, String payloadJson, OutboxStatus status) {
    public OutboxMessage { Objects.requireNonNull(id); Objects.requireNonNull(aggregateId); Objects.requireNonNull(payloadJson); Objects.requireNonNull(status); }
    public static OutboxMessage fromEvent(LearningAgreementHostConfirmedEvent event) {
        Objects.requireNonNull(event);
        String payload = String.format("{\"type\":\"HOST_CONFIRMED\",\"eventId\":\"%s\",\"agreementId\":\"%s\",\"studentId\":\"%s\",\"evidenceReference\":\"%s\",\"occurredOn\":\"%s\"}", event.eventId(), event.agreementId(), event.studentId(), event.evidenceReference(), event.occurredOn());
        return new OutboxMessage(event.eventId(), event.agreementId(), payload, OutboxStatus.PENDING);
    }
}
