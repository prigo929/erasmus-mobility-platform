package ro.uaic.feaa.erasmus.shared;

import java.util.Objects;
import java.util.UUID;

public record TaskId(UUID value) {
    public TaskId { Objects.requireNonNull(value); }
}
