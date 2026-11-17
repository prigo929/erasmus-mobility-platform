package ro.uaic.feaa.erasmus.agreement.infrastructure;

import java.util.Objects;
import java.util.UUID;
import ro.uaic.feaa.erasmus.agreement.domain.LearningAgreementApprovedEvent;

public record OutboxMessage(UUID id, UUID aggregateId, String payloadJson, OutboxStatus status) {
    public OutboxMessage { Objects.requireNonNull(id); Objects.requireNonNull(aggregateId); Objects.requireNonNull(payloadJson); Objects.requireNonNull(status); }
    public static OutboxMessage fromEvent(LearningAgreementApprovedEvent event) {
        Objects.requireNonNull(event);
        String payload = String.format("{\"eventId\":\"%s\",\"agreementId\":\"%s\",\"studentId\":\"%s\",\"occurredOn\":\"%s\"}", event.eventId(), event.agreementId(), event.studentId(), event.occurredOn());
        return new OutboxMessage(event.eventId(), event.agreementId(), payload, OutboxStatus.PENDING);
    }
}
