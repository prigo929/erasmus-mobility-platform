package ro.uaic.feaa.erasmus.shared;

import java.util.Objects;
import java.util.UUID;

public record EquivalenceId(UUID value) {
    public EquivalenceId { Objects.requireNonNull(value); }
}
