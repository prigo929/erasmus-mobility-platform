package ro.uaic.feaa.erasmus.shared;

import java.util.Objects;
import java.util.UUID;

public record StudentId(UUID value) {
    public StudentId { Objects.requireNonNull(value); }
}
