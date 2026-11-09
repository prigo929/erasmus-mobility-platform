package ro.uaic.feaa.erasmus.shared;

import java.util.Objects;
import java.util.UUID;

public record AgreementId(UUID value) {
    public AgreementId { Objects.requireNonNull(value); }
}
