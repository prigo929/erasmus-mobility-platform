"""Generate the P1 Java domain skeleton from the consolidated UML model."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "src/src/main/java/ro/uaic/feaa/erasmus"

def write(package, name, body, imports=""):
    path = ROOT / package.replace(".", "/") / f"{name}.java"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"package ro.uaic.feaa.erasmus.{package};\n\n{imports}{body}\n")

for name in ("StudentId", "AgreementId", "EquivalenceId", "TaskId", "ChecklistId"):
    write("shared", name, f"public record {name}(UUID value) {{\n    public {name} {{ Objects.requireNonNull(value); }}\n}}", "import java.util.Objects;\nimport java.util.UUID;\n\n")
write("shared", "ECTSCredits", "public record ECTSCredits(int value) {\n    public ECTSCredits { if (value < 0) throw new IllegalArgumentException(\"Negative credits\"); }\n    public boolean isMinimumMet() { return value >= 30; }\n    public ECTSCredits plus(ECTSCredits other) { return new ECTSCredits(Math.addExact(value, other.value)); }\n}")
write("shared", "ValidityWindow", "public record ValidityWindow(LocalDate startDate, LocalDate endDate) {\n    public ValidityWindow {\n        Objects.requireNonNull(startDate); Objects.requireNonNull(endDate);\n        if (endDate.isBefore(startDate)) throw new IllegalArgumentException(\"End before start\");\n    }\n    public boolean isWithinWindow(LocalDate date) { return !date.isBefore(startDate) && !date.isAfter(endDate); }\n}", "import java.time.LocalDate;\nimport java.util.Objects;\n\n")
write("shared", "AcademicYear", "public record AcademicYear(int startYear) {\n    public AcademicYear { if (startYear < 2000) throw new IllegalArgumentException(\"Invalid academic year\"); }\n}")
write("shared", "CourseCode", "public record CourseCode(String value) {\n    public CourseCode { if (value == null || value.isBlank()) throw new IllegalArgumentException(\"Empty course code\"); }\n}")

def enum(pkg, name, values):
    write(pkg, name, f"public enum {name} {{ {', '.join(values)} }}")
enum("agreement.domain", "LearningAgreementStatus", ["DRAFT", "SUBMITTED", "UNDER_REVIEW", "APPROVED_BY_FACULTY", "CONFIRMED_BY_HOST", "AMENDED", "CANCELLED"])
enum("equivalence.domain", "EquivalenceStatus", ["PROPOSED", "UNDER_EVALUATION", "APPROVED", "ACTIVE", "RETIRED"])
enum("preparation.domain", "TaskStatus", ["INITIALIZED", "PENDING_STUDENT_ACTION", "SUBMITTED_FOR_VERIFICATION", "COMPLETED", "OVERDUE", "ABANDONED"])
enum("preparation.domain", "TaskType", ["LEARNING_AGREEMENT_COUNTERSIGN", "HEALTH_INSURANCE_PROOF", "ACCOMMODATION_BOOKING", "VISA_CONFIRMATION", "GRANT_AGREEMENT_SIGNATURE"])
enum("agreement.infrastructure", "OutboxStatus", ["PENDING", "PUBLISHED"])

write("agreement.domain", "CourseLineTableA", "public record CourseLineTableA(UUID lineId, String hostCourseCode, String courseTitle, ECTSCredits credits) {\n    public CourseLineTableA { Objects.requireNonNull(lineId); Objects.requireNonNull(credits); }\n}", "import java.util.Objects;\nimport java.util.UUID;\nimport ro.uaic.feaa.erasmus.shared.ECTSCredits;\n\n")
write("agreement.domain", "CourseLineTableB", "public record CourseLineTableB(UUID lineId, String homeCourseCode, String equivalentCourseTitle, ECTSCredits credits) {\n    public CourseLineTableB { Objects.requireNonNull(lineId); Objects.requireNonNull(credits); }\n}", "import java.util.Objects;\nimport java.util.UUID;\nimport ro.uaic.feaa.erasmus.shared.ECTSCredits;\n\n")
write("agreement.domain", "LearningAgreementApprovedEvent", "public record LearningAgreementApprovedEvent(UUID eventId, UUID agreementId, UUID studentId, Instant occurredOn) {}", "import java.time.Instant;\nimport java.util.UUID;\n\n")
write("agreement.domain", "LearningAgreement", '''public final class LearningAgreement {
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
}''', "import java.time.Instant;\nimport java.util.*;\nimport ro.uaic.feaa.erasmus.shared.*;\n\n")
write("agreement.domain", "LearningAgreementRepository", "public interface LearningAgreementRepository {\n    Optional<LearningAgreement> findById(AgreementId id);\n    void save(LearningAgreement agreement);\n}", "import java.util.Optional;\nimport ro.uaic.feaa.erasmus.shared.AgreementId;\n\n")
write("agreement.domain", "EquivalenceVerificationResult", "public record EquivalenceVerificationResult(boolean equivalent, String message) {}")
write("agreement.domain", "IEquivalenceCatalogAdapter", "public interface IEquivalenceCatalogAdapter {\n    EquivalenceVerificationResult checkEquivalence(String sendCode, String hostCode);\n}")
write("agreement.domain", "IOutboxRepository", "public interface IOutboxRepository {\n    void save(OutboxMessage message);\n    List<OutboxMessage> findPendingMessages(int limit);\n    void markAsPublished(UUID id, Instant at);\n}", "import java.time.Instant;\nimport java.util.List;\nimport java.util.UUID;\nimport ro.uaic.feaa.erasmus.agreement.infrastructure.OutboxMessage;\n\n")
write("agreement.infrastructure", "OutboxMessage", "public record OutboxMessage(UUID id, UUID aggregateId, String payloadJson, OutboxStatus status) {\n    public OutboxMessage { Objects.requireNonNull(id); Objects.requireNonNull(aggregateId); Objects.requireNonNull(payloadJson); Objects.requireNonNull(status); }\n    public static OutboxMessage fromEvent(LearningAgreementApprovedEvent event) {\n        Objects.requireNonNull(event);\n        String payload = String.format(\"{\\\"eventId\\\":\\\"%s\\\",\\\"agreementId\\\":\\\"%s\\\",\\\"studentId\\\":\\\"%s\\\",\\\"occurredOn\\\":\\\"%s\\\"}\", event.eventId(), event.agreementId(), event.studentId(), event.occurredOn());\n        return new OutboxMessage(event.eventId(), event.agreementId(), payload, OutboxStatus.PENDING);\n    }\n}", "import java.util.Objects;\nimport java.util.UUID;\nimport ro.uaic.feaa.erasmus.agreement.domain.LearningAgreementApprovedEvent;\n\n")
write("equivalence.domain", "CourseSyllabus", "public record CourseSyllabus(CourseCode code, String courseName, ECTSCredits credits, UUID universityId) {\n    public CourseSyllabus { Objects.requireNonNull(code); Objects.requireNonNull(credits); Objects.requireNonNull(universityId); }\n}", "import java.util.Objects;\nimport java.util.UUID;\nimport ro.uaic.feaa.erasmus.shared.*;\n\n")
write("equivalence.domain", "AcademicEquivalence", '''public final class AcademicEquivalence {
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
}''', "import java.time.LocalDate;\nimport java.util.Objects;\nimport ro.uaic.feaa.erasmus.shared.*;\n\n")
write("equivalence.domain", "AcademicEquivalenceRepository", "public interface AcademicEquivalenceRepository {\n    Optional<AcademicEquivalence> findByCourseCodes(String sendCode, String hostCode);\n    Optional<AcademicEquivalence> findById(EquivalenceId id);\n    void save(AcademicEquivalence equivalence);\n}", "import java.util.Optional;\nimport ro.uaic.feaa.erasmus.shared.EquivalenceId;\n\n")
write("preparation.domain", "ChecklistTask", '''public final class ChecklistTask {
    private final TaskId taskId;
    private final TaskType taskType;
    private final String title;
    private TaskStatus status = TaskStatus.INITIALIZED;
    private final LocalDate deadline;
    private String proofDocumentUri;
    public ChecklistTask(TaskId taskId, TaskType taskType, String title, LocalDate deadline) {
        this.taskId = Objects.requireNonNull(taskId); this.taskType = Objects.requireNonNull(taskType);
        this.title = Objects.requireNonNull(title); this.deadline = Objects.requireNonNull(deadline);
    }
    public TaskId taskId() { return taskId; }
    public TaskType taskType() { return taskType; }
    public TaskStatus status() { return status; }
    public LocalDate deadline() { return deadline; }
    public String proofDocumentUri() { return proofDocumentUri; }
    public void assignToStudent() { requireStatus(TaskStatus.INITIALIZED); status = TaskStatus.PENDING_STUDENT_ACTION; }
    public void attachProof(String uri) { if (uri == null || uri.isBlank()) throw new IllegalArgumentException("Empty proof URI"); proofDocumentUri = uri; }
    public void markSubmitted() { if (status != TaskStatus.PENDING_STUDENT_ACTION && status != TaskStatus.OVERDUE) throw new IllegalStateException("Cannot submit"); if (proofDocumentUri == null) throw new IllegalStateException("Proof required"); status = TaskStatus.SUBMITTED_FOR_VERIFICATION; }
    public void markCompleted() { requireStatus(TaskStatus.SUBMITTED_FOR_VERIFICATION); status = TaskStatus.COMPLETED; }
    public void markOverdue() { if (status == TaskStatus.PENDING_STUDENT_ACTION || status == TaskStatus.SUBMITTED_FOR_VERIFICATION) status = TaskStatus.OVERDUE; }
    private void requireStatus(TaskStatus expected) { if (status != expected) throw new IllegalStateException("Expected " + expected); }
}''', "import java.time.LocalDate;\nimport java.util.Objects;\nimport ro.uaic.feaa.erasmus.shared.TaskId;\n\n")
write("preparation.domain", "MobilityChecklist", '''public final class MobilityChecklist {
    private final ChecklistId id;
    private final StudentId studentId;
    private final AgreementId agreementId;
    private final List<ChecklistTask> tasks = new ArrayList<>();
    public MobilityChecklist(ChecklistId id, StudentId studentId, AgreementId agreementId) {
        this.id = Objects.requireNonNull(id); this.studentId = Objects.requireNonNull(studentId); this.agreementId = Objects.requireNonNull(agreementId);
    }
    public ChecklistId id() { return id; }
    public StudentId studentId() { return studentId; }
    public AgreementId agreementId() { return agreementId; }
    public List<ChecklistTask> tasks() { return List.copyOf(tasks); }
    public void initializeDefaultPreparationTasks() {
        if (!tasks.isEmpty()) throw new IllegalStateException("Already initialized");
        for (TaskType type : TaskType.values()) { ChecklistTask task = new ChecklistTask(new TaskId(UUID.randomUUID()), type, type.name(), LocalDate.now().plusMonths(3)); task.assignToStudent(); tasks.add(task); }
    }
    public void completeTask(TaskId taskId) { tasks.stream().filter(t -> t.taskId().equals(taskId)).findFirst().orElseThrow().markCompleted(); }
    public boolean areMandatoryTasksComplete() { return !tasks.isEmpty() && tasks.stream().allMatch(t -> t.status() == TaskStatus.COMPLETED); }
    public void flagOverdueTasks(LocalDate asOf) { for (ChecklistTask task : tasks) if (asOf.isAfter(task.deadline())) task.markOverdue(); }
}''', "import java.time.LocalDate;\nimport java.util.*;\nimport ro.uaic.feaa.erasmus.shared.*;\n\n")
write("preparation.domain", "MobilityChecklistRepository", "public interface MobilityChecklistRepository {\n    void save(MobilityChecklist checklist);\n    Optional<MobilityChecklist> findByAgreementId(AgreementId agreementId);\n    Optional<MobilityChecklist> findByStudentId(StudentId studentId);\n}", "import java.util.Optional;\nimport ro.uaic.feaa.erasmus.shared.*;\n\n")
write("preparation.domain", "IProcessedEventRepository", "public interface IProcessedEventRepository {\n    boolean existsById(UUID eventId);\n    void recordEvent(UUID eventId, Instant at);\n}", "import java.time.Instant;\nimport java.util.UUID;\n\n")
print("Generated Java domain skeleton")
