package ro.uaic.feaa.erasmus.preparation.domain;

import java.time.LocalDate;
import java.util.Objects;
import ro.uaic.feaa.erasmus.shared.TaskId;

public final class ChecklistTask {
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
}
