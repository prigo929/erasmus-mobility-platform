package ro.uaic.feaa.erasmus.agreement.domain;

import java.time.Instant;
import java.util.*;
import ro.uaic.feaa.erasmus.shared.*;

public final class LearningAgreement {
    private final AgreementId id;
    private final StudentId studentId;
    private final AcademicYear academicYear;
    private LearningAgreementStatus status = LearningAgreementStatus.DRAFT;
    private final List<CourseLineTableA> linesTableA = new ArrayList<>();
    private final List<CourseLineTableB> linesTableB = new ArrayList<>();

    public LearningAgreement(AgreementId id, StudentId studentId, AcademicYear academicYear) {
        this.id = Objects.requireNonNull(id);
        this.studentId = Objects.requireNonNull(studentId);
        this.academicYear = Objects.requireNonNull(academicYear);
    }
    public AgreementId id() { return id; }
    public StudentId studentId() { return studentId; }
    public AcademicYear academicYear() { return academicYear; }
    public LearningAgreementStatus status() { return status; }
    public List<CourseLineTableA> linesTableA() { return List.copyOf(linesTableA); }
    public List<CourseLineTableB> linesTableB() { return List.copyOf(linesTableB); }
    public void addTableALine(CourseLineTableA line) { requireDraft(); linesTableA.add(Objects.requireNonNull(line)); }
    public void addTableBLine(CourseLineTableB line) { requireDraft(); linesTableB.add(Objects.requireNonNull(line)); }
    private void requireDraft() { if (status != LearningAgreementStatus.DRAFT && status != LearningAgreementStatus.AMENDED) throw new IllegalStateException("Lines are locked"); }
    public ECTSCredits calculateTotalCreditsTableA() { return linesTableA.stream().map(CourseLineTableA::credits).reduce(new ECTSCredits(0), ECTSCredits::plus); }
    public ECTSCredits calculateTotalCreditsTableB() { return linesTableB.stream().map(CourseLineTableB::credits).reduce(new ECTSCredits(0), ECTSCredits::plus); }
    public boolean hasCreditParity() { return calculateTotalCreditsTableA().equals(calculateTotalCreditsTableB()); }
    public void submit() {
        requireDraft();
        if (!hasCreditParity() || !calculateTotalCreditsTableA().isMinimumMet()) throw new IllegalStateException("Credit parity and 30 ECTS required");
        status = LearningAgreementStatus.SUBMITTED;
    }
    public void resubmitAmendedDraft() { if (status != LearningAgreementStatus.AMENDED) throw new IllegalStateException("Expected AMENDED"); submit(); }
    public void assignCoordinator(UUID coordinatorId) { Objects.requireNonNull(coordinatorId); requireStatus(LearningAgreementStatus.SUBMITTED); status = LearningAgreementStatus.UNDER_REVIEW; }
    public void requestChanges(String reason) { Objects.requireNonNull(reason); requireStatus(LearningAgreementStatus.UNDER_REVIEW); status = LearningAgreementStatus.DRAFT; }
    public LearningAgreementApprovedEvent approve(UUID coordinatorId) {
        Objects.requireNonNull(coordinatorId); requireStatus(LearningAgreementStatus.UNDER_REVIEW);
        if (!hasCreditParity()) throw new IllegalStateException("Credit parity required");
        status = LearningAgreementStatus.APPROVED_BY_FACULTY;
        return new LearningAgreementApprovedEvent(UUID.randomUUID(), id.value(), studentId.value(), Instant.now());
    }
    public void confirmByHost(String signatureRef) { Objects.requireNonNull(signatureRef); requireStatus(LearningAgreementStatus.APPROVED_BY_FACULTY); status = LearningAgreementStatus.CONFIRMED_BY_HOST; }
    public void requestAmendment(String reason) { Objects.requireNonNull(reason); if (status != LearningAgreementStatus.APPROVED_BY_FACULTY && status != LearningAgreementStatus.CONFIRMED_BY_HOST) throw new IllegalStateException("Cannot amend"); status = LearningAgreementStatus.AMENDED; }
    public void cancel() { status = LearningAgreementStatus.CANCELLED; }
    private void requireStatus(LearningAgreementStatus expected) { if (status != expected) throw new IllegalStateException("Expected " + expected); }
}
