package ro.uaic.feaa.erasmus.platform;

import java.time.LocalDate;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/** Persistence snapshots for the first runnable, single-process platform prototype. */
public final class PlatformState {
    private PlatformState() {}

    public enum AgreementStatus { DRAFT, SUBMITTED, UNDER_REVIEW, APPROVED_BY_FACULTY, CONFIRMED_BY_HOST, CANCELLED }
    public enum EquivalenceStatus { PROPOSED, UNDER_EVALUATION, ACTIVE, REJECTED, RETIRED }
    public enum TaskStatus { PENDING_STUDENT_ACTION, SUBMITTED_FOR_VERIFICATION, COMPLETED, OVERDUE, ABANDONED }
    public enum TaskType { LEARNING_AGREEMENT_COUNTERSIGN, HEALTH_INSURANCE_PROOF, ACCOMMODATION_BOOKING, VISA_CONFIRMATION, GRANT_AGREEMENT_SIGNATURE }

    public record CourseLine(UUID lineId, String code, String title, int credits) {}
    public record Agreement(UUID id, UUID studentId, UUID mobilityId, String academicYear,
                            LocalDate periodStart, LocalDate periodEnd, String hostUniversity,
                            List<CourseLine> tableA, List<CourseLine> tableB,
                            AgreementStatus status, String lastDecisionReason,
                            String hostEvidenceReference, long version) {
        public Agreement { tableA = List.copyOf(tableA); tableB = List.copyOf(tableB); }
        public Agreement withStatus(AgreementStatus next) {
            return new Agreement(id, studentId, mobilityId, academicYear, periodStart, periodEnd,
                hostUniversity, tableA, tableB, next, lastDecisionReason, hostEvidenceReference, version + 1);
        }
        public Agreement withDecision(AgreementStatus next, String reason) {
            return new Agreement(id, studentId, mobilityId, academicYear, periodStart, periodEnd,
                hostUniversity, tableA, tableB, next, reason, hostEvidenceReference, version + 1);
        }
        public Agreement withHostConfirmation(String evidenceReference) {
            return new Agreement(id, studentId, mobilityId, academicYear, periodStart, periodEnd,
                hostUniversity, tableA, tableB, AgreementStatus.CONFIRMED_BY_HOST, lastDecisionReason,
                evidenceReference, version + 1);
        }
        public Agreement withLines(List<CourseLine> nextTableA, List<CourseLine> nextTableB) {
            return new Agreement(id, studentId, mobilityId, academicYear, periodStart, periodEnd,
                hostUniversity, nextTableA, nextTableB, status, lastDecisionReason, hostEvidenceReference, version + 1);
        }
    }
    public record Equivalence(UUID id, String homeCode, String hostCode, int homeCredits,
                              int hostCredits, LocalDate validFrom, LocalDate validTo,
                              EquivalenceStatus status, Integer score, String rationale, long version) {
        public Equivalence withStatus(EquivalenceStatus next, Integer nextScore, String nextRationale) {
            return new Equivalence(id, homeCode, hostCode, homeCredits, hostCredits, validFrom, validTo,
                next, nextScore, nextRationale, version + 1);
        }
    }
    public record Task(UUID id, TaskType type, TaskStatus status, LocalDate deadline, String proofUri, String reviewNote) {
        public Task withStatus(TaskStatus next, String proof) { return new Task(id, type, next, deadline, proof, reviewNote); }
        public Task rejected(String reason) { return new Task(id, type, TaskStatus.PENDING_STUDENT_ACTION, deadline, null, reason); }
    }
    public record Checklist(UUID mobilityId, UUID studentId, UUID agreementId,
                            List<Task> tasks, boolean cancelled, Set<UUID> processedEventIds,
                            long lastSourceVersion, long version) {
        public Checklist { tasks = List.copyOf(tasks); processedEventIds = Set.copyOf(processedEventIds); }
        public Checklist next(List<Task> nextTasks, boolean nextCancelled, Set<UUID> events, long sourceVersion) {
            return new Checklist(mobilityId, studentId, agreementId, nextTasks, nextCancelled, events,
                Math.max(lastSourceVersion, sourceVersion), version + 1);
        }
    }
    public record OutboxEvent(UUID id, UUID mobilityId, UUID agreementId, String type,
                              long sourceVersion, LocalDate occurredOn, boolean delivered) {
        public OutboxEvent asDelivered() { return new OutboxEvent(id, mobilityId, agreementId, type, sourceVersion, occurredOn, true); }
    }
}
