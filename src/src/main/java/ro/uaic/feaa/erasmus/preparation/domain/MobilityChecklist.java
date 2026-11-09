package ro.uaic.feaa.erasmus.preparation.domain;

import java.time.LocalDate;
import java.util.*;
import ro.uaic.feaa.erasmus.shared.*;

public final class MobilityChecklist {
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
}
