package ro.uaic.feaa.erasmus.agreement.domain;

import java.time.Instant;
import java.util.UUID;

public record LearningAgreementApprovedEvent(UUID eventId, UUID agreementId, UUID studentId, Instant occurredOn) {}
