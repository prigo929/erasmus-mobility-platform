package ro.uaic.feaa.erasmus.shared;

import java.time.LocalDate;
import java.util.Objects;

public record ValidityWindow(LocalDate startDate, LocalDate endDate) {
    public ValidityWindow {
        Objects.requireNonNull(startDate); Objects.requireNonNull(endDate);
        if (endDate.isBefore(startDate)) throw new IllegalArgumentException("End before start");
    }
    public boolean isWithinWindow(LocalDate date) { return !date.isBefore(startDate) && !date.isAfter(endDate); }
}
