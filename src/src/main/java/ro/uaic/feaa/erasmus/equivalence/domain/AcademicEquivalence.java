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
    public void approve() { requireStatus(EquivalenceStatus.UNDER_EVALUATION); status = EquivalenceStatus.APPROVED; }
    public void activate() { requireStatus(EquivalenceStatus.APPROVED); status = EquivalenceStatus.ACTIVE; }
    public void retire(LocalDate effectiveDate) { Objects.requireNonNull(effectiveDate); status = EquivalenceStatus.RETIRED; }
    private void requireStatus(EquivalenceStatus expected) { if (status != expected) throw new IllegalStateException("Expected " + expected); }
}
