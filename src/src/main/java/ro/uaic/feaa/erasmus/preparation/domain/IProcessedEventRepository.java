package ro.uaic.feaa.erasmus.preparation.domain;

import java.time.Instant;
import java.util.UUID;

public interface IProcessedEventRepository {
    boolean existsById(UUID eventId);
    void recordEvent(UUID eventId, Instant at);
}
