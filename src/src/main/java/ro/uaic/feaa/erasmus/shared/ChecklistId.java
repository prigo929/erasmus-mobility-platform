package ro.uaic.feaa.erasmus.shared;

import java.util.Objects;
import java.util.UUID;

public record ChecklistId(UUID value) {
    public ChecklistId { Objects.requireNonNull(value); }
}
