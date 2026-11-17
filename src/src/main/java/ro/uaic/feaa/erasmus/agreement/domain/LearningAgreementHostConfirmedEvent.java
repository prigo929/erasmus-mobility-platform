package ro.uaic.feaa.erasmus.agreement.domain;

import java.time.Instant;
import java.util.UUID;

public record LearningAgreementHostConfirmedEvent(UUID eventId, UUID agreementId, UUID studentId,
                                                   String evidenceReference, Instant occurredOn) {}
