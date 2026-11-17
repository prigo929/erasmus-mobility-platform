package ro.uaic.feaa.erasmus.equivalence.domain;

import java.time.LocalDate;
import java.util.Objects;
import ro.uaic.feaa.erasmus.shared.*;

public final class AcademicEquivalence {
    private final EquivalenceId id;
    private final CourseSyllabus sendCourse;
    private final CourseSyllabus hostCourse;
    private final ECTSCredits recognizedCredits;
    private final ValidityWindow validityWindow;
    private EquivalenceStatus status = EquivalenceStatus.PROPOSED;
    public AcademicEquivalence(EquivalenceId id, CourseSyllabus sendCourse, CourseSyllabus hostCourse, ECTSCredits recognizedCredits, ValidityWindow validityWindow) {
        this.id = Objects.requireNonNull(id); this.sendCourse = Objects.requireNonNull(sendCourse); this.hostCourse = Objects.requireNonNull(hostCourse);
        this.recognizedCredits = Objects.requireNonNull(recognizedCredits); this.validityWindow = Objects.requireNonNull(validityWindow);
    }
    public EquivalenceId id() { return id; }
    public EquivalenceStatus status() { return status; }
    public boolean isCurrentlyValid(LocalDate asOf) { return status == EquivalenceStatus.ACTIVE && validityWindow.isWithinWindow(asOf); }
    public boolean matchesCourses(String send, String host) { return sendCourse.code().value().equals(send) && hostCourse.code().value().equals(host); }
    public void initiateEvaluation() { requireStatus(EquivalenceStatus.PROPOSED); status = EquivalenceStatus.UNDER_EVALUATION; }
    public void evaluateAndPublish(int score, String rationale, LocalDate mobilityStart, LocalDate mobilityEnd) {
        requireStatus(EquivalenceStatus.UNDER_EVALUATION);
        Objects.requireNonNull(rationale); Objects.requireNonNull(mobilityStart); Objects.requireNonNull(mobilityEnd);
        if (score < 80 || score > 100) throw new IllegalArgumentException("Score must be between 80 and 100");
        if (rationale.isBlank()) throw new IllegalArgumentException("Rationale is required");
        if (!recognizedCredits.equals(sendCourse.credits()) || !recognizedCredits.equals(hostCourse.credits()))
            throw new IllegalStateException("Equivalent course credits must match");
        if (mobilityStart.isAfter(mobilityEnd) || !validityWindow.isWithinWindow(mobilityStart) || !validityWindow.isWithinWindow(mobilityEnd))
            throw new IllegalArgumentException("Validity must cover the full mobility period");
        status = EquivalenceStatus.ACTIVE;
    }
    public void reject(String reason) {
        requireStatus(EquivalenceStatus.UNDER_EVALUATION);
        if (reason == null || reason.isBlank()) throw new IllegalArgumentException("Rejection reason is required");
        status = EquivalenceStatus.REJECTED;
    }
    public void retire(LocalDate effectiveDate) { Objects.requireNonNull(effectiveDate); status = EquivalenceStatus.RETIRED; }
    private void requireStatus(EquivalenceStatus expected) { if (status != expected) throw new IllegalStateException("Expected " + expected); }
}
