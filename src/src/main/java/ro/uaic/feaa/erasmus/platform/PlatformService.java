package ro.uaic.feaa.erasmus.platform;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import ro.uaic.feaa.erasmus.api.dto.ApiDtos.*;
import ro.uaic.feaa.erasmus.agreement.domain.CourseLineTableA;
import ro.uaic.feaa.erasmus.agreement.domain.CourseLineTableB;
import ro.uaic.feaa.erasmus.agreement.domain.LearningAgreement;
import ro.uaic.feaa.erasmus.equivalence.domain.AcademicEquivalence;
import ro.uaic.feaa.erasmus.equivalence.domain.CourseSyllabus;
import ro.uaic.feaa.erasmus.shared.*;
import ro.uaic.feaa.erasmus.platform.PlatformState.*;

@Service
public class PlatformService {
    private static final String AGREEMENT = "agreement";
    private static final String EQUIVALENCE = "equivalence";
    private static final String CHECKLIST = "checklist";
    private static final String OUTBOX = "outbox";
    private static final int MINIMUM_ECTS = 30;
    private final JsonStateStore store;
    public PlatformService(JsonStateStore store) { this.store = store; }

    @Transactional
    public Agreement createAgreement(CreateAgreementRequest request) {
        if (request.periodEnd().isBefore(request.periodStart())) throw new IllegalArgumentException("Perioada mobilității este invalidă.");
        if (!request.academicYear().matches("\\d{4}-\\d{4}") ||
            Integer.parseInt(request.academicYear().substring(5)) != Integer.parseInt(request.academicYear().substring(0, 4)) + 1)
            throw new IllegalArgumentException("Anul academic trebuie să fie consecutiv, în formatul AAAA-AAAA.");
        if (store.findAll(AGREEMENT, Agreement.class).stream().anyMatch(a -> a.mobilityId().equals(request.mobilityId())))
            throw new IllegalStateException("Există deja un acord pentru această mobilitate.");
        Agreement agreement = new Agreement(UUID.randomUUID(), request.studentId(), request.mobilityId(),
            request.academicYear(), request.periodStart(), request.periodEnd(), request.hostUniversity(),
            lines(request.tableA()), lines(request.tableB()), AgreementStatus.DRAFT, null, null, 1);
        store.insert(AGREEMENT, agreement.id(), agreement, 1);
        return agreement;
    }

    public Agreement getAgreement(UUID id) { return required(AGREEMENT, id, Agreement.class); }

    @Transactional
    public Agreement replaceAgreementLines(UUID id, ReplaceLinesRequest request) {
        Agreement current = requireVersion(getAgreement(id), request.expectedVersion());
        requireStatus(current.status(), AgreementStatus.DRAFT);
        Agreement next = current.withLines(lines(request.tableA()), lines(request.tableB()));
        store.update(AGREEMENT, id, current.version(), next, next.version());
        return next;
    }

    @Transactional
    public Agreement submitAgreement(UUID id, VersionRequest request) {
        Agreement agreement = requireVersion(getAgreement(id), request.expectedVersion());
        requireStatus(agreement.status(), AgreementStatus.DRAFT);
        if (agreement.tableA().isEmpty() || agreement.tableA().size() != agreement.tableB().size())
            throw new IllegalStateException("Fiecare curs gazdă trebuie să aibă exact un curs de origine.");
        Map<UUID, CourseLine> homeLines = uniqueLines(agreement.tableB());
        Map<UUID, CourseLine> hostLines = uniqueLines(agreement.tableA());
        if (!homeLines.keySet().equals(hostLines.keySet()))
            throw new IllegalStateException("Mapările dintre cursurile de origine și cele gazdă nu sunt 1:1.");
        int total = 0;
        for (UUID lineId : homeLines.keySet()) {
            CourseLine home = homeLines.get(lineId), host = hostLines.get(lineId);
            if (home.credits() != host.credits()) throw new IllegalStateException("Creditele cursurilor mapate trebuie să fie egale.");
            boolean eligible = store.findAll(EQUIVALENCE, Equivalence.class).stream().anyMatch(e ->
                e.status() == EquivalenceStatus.ACTIVE && e.homeCode().equals(home.code()) && e.hostCode().equals(host.code()) &&
                e.homeCredits() == home.credits() && e.hostCredits() == host.credits() &&
                !agreement.periodStart().isBefore(e.validFrom()) && !agreement.periodEnd().isAfter(e.validTo()));
            if (!eligible) throw new IllegalStateException("Echivalarea nu este activă pentru întreaga perioadă: " + home.code() + " → " + host.code());
            total = Math.addExact(total, home.credits());
        }
        if (total < MINIMUM_ECTS) throw new IllegalStateException("Acordul trebuie să includă cel puțin 30 ECTS.");
        validateWithDomain(agreement);
        return transitionAgreement(agreement, AgreementStatus.SUBMITTED);
    }

    @Transactional
    public Agreement beginReview(UUID id, VersionRequest request) {
        Agreement agreement = requireVersion(getAgreement(id), request.expectedVersion());
        requireStatus(agreement.status(), AgreementStatus.SUBMITTED);
        return transitionAgreement(agreement, AgreementStatus.UNDER_REVIEW);
    }

    @Transactional
    public Agreement approve(UUID id, ReviewRequest request) {
        Agreement agreement = requireVersion(getAgreement(id), request.expectedVersion());
        requireStatus(agreement.status(), AgreementStatus.UNDER_REVIEW);
        return transitionAgreement(agreement, AgreementStatus.APPROVED_BY_FACULTY);
    }

    @Transactional
    public Agreement requestChanges(UUID id, DecisionRequest request) {
        Agreement agreement = requireVersion(getAgreement(id), request.expectedVersion());
        requireStatus(agreement.status(), AgreementStatus.UNDER_REVIEW);
        Agreement next = agreement.withDecision(AgreementStatus.DRAFT, request.reason());
        store.update(AGREEMENT, id, agreement.version(), next, next.version());
        return next;
    }

    @Transactional
    public Agreement confirmHost(UUID id, HostConfirmationRequest request) {
        Agreement agreement = requireVersion(getAgreement(id), request.expectedVersion());
        requireStatus(agreement.status(), AgreementStatus.APPROVED_BY_FACULTY);
        if (request.evidenceReference().isBlank()) throw new IllegalArgumentException("Este necesară referința dovezii gazdei.");
        Agreement confirmed = agreement.withHostConfirmation(request.evidenceReference());
        store.update(AGREEMENT, id, agreement.version(), confirmed, confirmed.version());
        OutboxEvent event = new OutboxEvent(UUID.randomUUID(), agreement.mobilityId(), id,
            "HOST_CONFIRMED", confirmed.version(), LocalDate.now(), false);
        store.insert(OUTBOX, event.id(), event, 1);
        return confirmed;
    }

    @Transactional
    public Agreement cancel(UUID id, VersionRequest request) {
        Agreement agreement = requireVersion(getAgreement(id), request.expectedVersion());
        if (agreement.status() == AgreementStatus.CANCELLED) throw new IllegalStateException("Acordul este deja anulat.");
        Agreement cancelled = agreement.withStatus(AgreementStatus.CANCELLED);
        store.update(AGREEMENT, id, agreement.version(), cancelled, cancelled.version());
        OutboxEvent event = new OutboxEvent(UUID.randomUUID(), agreement.mobilityId(), id,
            "CANCELLED", cancelled.version(), LocalDate.now(), false);
        store.insert(OUTBOX, event.id(), event, 1);
        return cancelled;
    }

    @Transactional
    public Equivalence propose(CreateEquivalenceRequest request) {
        if (request.validTo().isBefore(request.validFrom())) throw new IllegalArgumentException("Perioada echivalării este invalidă.");
        if (request.homeCode().equals(request.hostCode())) throw new IllegalArgumentException("Codurile cursurilor trebuie să fie diferite.");
        Equivalence value = new Equivalence(UUID.randomUUID(), request.homeCode(), request.hostCode(),
            request.homeCredits(), request.hostCredits(), request.validFrom(), request.validTo(),
            EquivalenceStatus.PROPOSED, null, null, 1);
        store.insert(EQUIVALENCE, value.id(), value, 1);
        return value;
    }

    public List<Equivalence> equivalences() { return store.findAll(EQUIVALENCE, Equivalence.class); }
    public Equivalence getEquivalence(UUID id) { return required(EQUIVALENCE, id, Equivalence.class); }

    @Transactional
    public Equivalence beginEvaluation(UUID id, VersionRequest request) {
        Equivalence current = requireVersion(required(EQUIVALENCE, id, Equivalence.class), request.expectedVersion());
        requireStatus(current.status(), EquivalenceStatus.PROPOSED);
        Equivalence next = current.withStatus(EquivalenceStatus.UNDER_EVALUATION, null, null);
        store.update(EQUIVALENCE, id, current.version(), next, next.version());
        return next;
    }

    @Transactional
    public synchronized Equivalence evaluateAndPublish(UUID id, EvaluationRequest request) {
        Equivalence current = requireVersion(required(EQUIVALENCE, id, Equivalence.class), request.expectedVersion());
        requireStatus(current.status(), EquivalenceStatus.UNDER_EVALUATION);
        if (request.score() < 80) throw new IllegalStateException("Scorul minim pentru publicare este 80 din 100.");
        if (current.homeCredits() != current.hostCredits()) throw new IllegalStateException("Creditele cursurilor trebuie să fie egale.");
        boolean overlap = store.findAll(EQUIVALENCE, Equivalence.class).stream().anyMatch(other ->
            !other.id().equals(id) && other.status() == EquivalenceStatus.ACTIVE &&
            other.homeCode().equals(current.homeCode()) && other.hostCode().equals(current.hostCode()) &&
            !other.validTo().isBefore(current.validFrom()) && !other.validFrom().isAfter(current.validTo()));
        if (overlap) throw new IllegalStateException("Există deja o echivalare activă cu perioadă suprapusă.");
        AcademicEquivalence domain = new AcademicEquivalence(new EquivalenceId(id),
            new CourseSyllabus(new CourseCode(current.homeCode()), current.homeCode(), new ECTSCredits(current.homeCredits()), new UUID(0, 1)),
            new CourseSyllabus(new CourseCode(current.hostCode()), current.hostCode(), new ECTSCredits(current.hostCredits()), new UUID(0, 2)),
            new ECTSCredits(current.homeCredits()), new ValidityWindow(current.validFrom(), current.validTo()));
        domain.initiateEvaluation();
        domain.evaluateAndPublish(request.score(), request.rationale(), current.validFrom(), current.validTo());
        Equivalence next = current.withStatus(EquivalenceStatus.ACTIVE, request.score(), request.rationale());
        store.update(EQUIVALENCE, id, current.version(), next, next.version());
        return next;
    }

    @Transactional
    public Equivalence rejectEquivalence(UUID id, DecisionRequest request) {
        Equivalence current = requireVersion(getEquivalence(id), request.expectedVersion());
        requireStatus(current.status(), EquivalenceStatus.UNDER_EVALUATION);
        Equivalence next = current.withStatus(EquivalenceStatus.REJECTED, null, request.reason());
        store.update(EQUIVALENCE, id, current.version(), next, next.version());
        return next;
    }

    @Transactional
    public Equivalence retireEquivalence(UUID id, VersionRequest request) {
        Equivalence current = requireVersion(getEquivalence(id), request.expectedVersion());
        requireStatus(current.status(), EquivalenceStatus.ACTIVE);
        Equivalence next = current.withStatus(EquivalenceStatus.RETIRED, current.score(), current.rationale());
        store.update(EQUIVALENCE, id, current.version(), next, next.version());
        return next;
    }

    public VerificationResponse verify(String homeCode, String hostCode, LocalDate onDate) {
        boolean eligible = store.findAll(EQUIVALENCE, Equivalence.class).stream().anyMatch(e ->
            e.status() == EquivalenceStatus.ACTIVE && e.homeCode().equals(homeCode) && e.hostCode().equals(hostCode) &&
            !onDate.isBefore(e.validFrom()) && !onDate.isAfter(e.validTo()) && e.homeCredits() == e.hostCredits());
        return new VerificationResponse(eligible ? "ELIGIBLE" : "INELIGIBLE",
            eligible ? "Echivalare activă pentru data selectată." : "Nu există o echivalare activă pentru cursurile și data selectate.");
    }

    @Transactional
    public Checklist createChecklist(CreateMobilityRequest request) {
        Agreement agreement = getAgreement(request.agreementId());
        if (!agreement.studentId().equals(request.studentId()) || !agreement.mobilityId().equals(request.mobilityId()))
            throw new IllegalArgumentException("Mobilitatea și studentul trebuie să corespundă acordului.");
        if (store.findAll(CHECKLIST, Checklist.class).stream().anyMatch(c -> c.mobilityId().equals(request.mobilityId())))
            throw new IllegalStateException("Checklistul pentru această mobilitate există deja.");
        List<Task> tasks = Arrays.stream(TaskType.values()).map(type ->
            new Task(UUID.randomUUID(), type, TaskStatus.PENDING_STUDENT_ACTION, LocalDate.now().plusMonths(3), null, null)).toList();
        Checklist checklist = new Checklist(request.mobilityId(), request.studentId(), request.agreementId(),
            tasks, false, Set.of(), 0, 1);
        store.insert(CHECKLIST, checklist.mobilityId(), checklist, 1);
        return checklist;
    }

    public Checklist checklist(UUID mobilityId) { return required(CHECKLIST, mobilityId, Checklist.class); }

    @Transactional
    public Checklist submitProof(UUID mobilityId, UUID taskId, ProofRequest request) {
        Checklist current = checklist(mobilityId);
        if (current.cancelled()) throw new IllegalStateException("Mobilitatea este anulată.");
        List<Task> tasks = current.tasks().stream().map(task -> {
            if (!task.id().equals(taskId)) return task;
            if (task.status() != TaskStatus.PENDING_STUDENT_ACTION && task.status() != TaskStatus.OVERDUE)
                throw new IllegalStateException("Sarcina nu acceptă dovezi în starea curentă.");
            return task.withStatus(TaskStatus.SUBMITTED_FOR_VERIFICATION, request.proofUri());
        }).toList();
        if (tasks.stream().noneMatch(task -> task.id().equals(taskId))) throw notFound("Sarcina nu a fost găsită.");
        return saveChecklist(current, tasks, current.cancelled(), current.processedEventIds(), current.lastSourceVersion());
    }

    @Transactional
    public Checklist completeTask(UUID mobilityId, UUID taskId) {
        Checklist current = checklist(mobilityId);
        List<Task> tasks = current.tasks().stream().map(task -> {
            if (!task.id().equals(taskId)) return task;
            if (task.status() != TaskStatus.SUBMITTED_FOR_VERIFICATION) throw new IllegalStateException("Dovada trebuie trimisă înainte de verificare.");
            return task.withStatus(TaskStatus.COMPLETED, task.proofUri());
        }).toList();
        if (tasks.stream().noneMatch(task -> task.id().equals(taskId))) throw notFound("Sarcina nu a fost găsită.");
        return saveChecklist(current, tasks, current.cancelled(), current.processedEventIds(), current.lastSourceVersion());
    }

    @Transactional
    public Checklist rejectTaskProof(UUID mobilityId, UUID taskId, DecisionRequest request) {
        Checklist current = checklist(mobilityId);
        List<Task> tasks = current.tasks().stream().map(task -> {
            if (!task.id().equals(taskId)) return task;
            if (task.status() != TaskStatus.SUBMITTED_FOR_VERIFICATION) throw new IllegalStateException("Nu există o dovadă în așteptarea verificării.");
            return task.rejected(request.reason());
        }).toList();
        if (tasks.stream().noneMatch(task -> task.id().equals(taskId))) throw notFound("Sarcina nu a fost găsită.");
        return saveChecklist(current, tasks, current.cancelled(), current.processedEventIds(), current.lastSourceVersion());
    }

    @Transactional
    public int flagOverdueTasks(LocalDate asOf) {
        int changed = 0;
        for (Checklist current : store.findAll(CHECKLIST, Checklist.class)) {
            List<Task> tasks = current.tasks().stream().map(task -> {
                if (!current.cancelled() && task.status() == TaskStatus.PENDING_STUDENT_ACTION && asOf.isAfter(task.deadline()))
                    return task.withStatus(TaskStatus.OVERDUE, task.proofUri());
                return task;
            }).toList();
            if (!tasks.equals(current.tasks())) {
                saveChecklist(current, tasks, current.cancelled(), current.processedEventIds(), current.lastSourceVersion());
                changed++;
            }
        }
        return changed;
    }

    @Transactional
    public int processOutbox() {
        int delivered = 0;
        for (OutboxEvent event : store.findAll(OUTBOX, OutboxEvent.class)) {
            if (event.delivered()) continue;
            Optional<Checklist> found = store.find(CHECKLIST, event.mobilityId(), Checklist.class);
            if (found.isEmpty()) continue;
            Checklist current = found.get();
            if (!current.agreementId().equals(event.agreementId())) continue;
            if (current.processedEventIds().contains(event.id())) {
                store.update(OUTBOX, event.id(), 1, event.asDelivered(), 2);
                delivered++;
                continue;
            }
            Set<UUID> eventIds = new HashSet<>(current.processedEventIds());
            eventIds.add(event.id());
            List<Task> tasks = current.tasks();
            boolean cancelled = current.cancelled();
            if (event.sourceVersion() >= current.lastSourceVersion()) {
                if (event.type().equals("HOST_CONFIRMED") && !cancelled) {
                    tasks = tasks.stream().map(task -> task.type() == TaskType.LEARNING_AGREEMENT_COUNTERSIGN
                        ? task.withStatus(TaskStatus.COMPLETED, "host-confirmation:" + event.agreementId()) : task).toList();
                } else if (event.type().equals("CANCELLED")) {
                    cancelled = true;
                    tasks = tasks.stream().map(task -> task.status() == TaskStatus.COMPLETED ? task
                        : task.withStatus(TaskStatus.ABANDONED, task.proofUri())).toList();
                }
            }
            saveChecklist(current, tasks, cancelled, eventIds, event.sourceVersion());
            store.update(OUTBOX, event.id(), 1, event.asDelivered(), 2);
            delivered++;
        }
        return delivered;
    }

    public long pendingOutboxCount() {
        return store.findAll(OUTBOX, OutboxEvent.class).stream().filter(event -> !event.delivered()).count();
    }

    private Agreement transitionAgreement(Agreement current, AgreementStatus nextStatus) {
        Agreement next = current.withStatus(nextStatus);
        store.update(AGREEMENT, current.id(), current.version(), next, next.version());
        return next;
    }
    private void validateWithDomain(Agreement agreement) {
        int year = Integer.parseInt(agreement.academicYear().substring(0, 4));
        LearningAgreement domain = new LearningAgreement(new AgreementId(agreement.id()),
            new StudentId(agreement.studentId()), new AcademicYear(year));
        agreement.tableA().forEach(line -> domain.addTableALine(new CourseLineTableA(line.lineId(), line.code(), line.title(), new ECTSCredits(line.credits()))));
        agreement.tableB().forEach(line -> domain.addTableBLine(new CourseLineTableB(line.lineId(), line.code(), line.title(), new ECTSCredits(line.credits()))));
        domain.submit();
    }
    private Checklist saveChecklist(Checklist current, List<Task> tasks, boolean cancelled, Set<UUID> events, long sourceVersion) {
        Checklist next = current.next(tasks, cancelled, events, sourceVersion);
        store.update(CHECKLIST, current.mobilityId(), current.version(), next, next.version());
        return next;
    }
    private List<CourseLine> lines(List<CourseLineRequest> lines) {
        return lines.stream().map(line -> new CourseLine(line.lineId(), line.code(), line.title(), line.credits())).toList();
    }
    private Map<UUID, CourseLine> uniqueLines(List<CourseLine> lines) {
        Map<UUID, CourseLine> result = new HashMap<>();
        for (CourseLine line : lines) if (result.putIfAbsent(line.lineId(), line) != null)
            throw new IllegalStateException("Un identificator de mapare este folosit de mai multe ori.");
        return result;
    }
    private Agreement requireVersion(Agreement value, long expected) {
        if (value.version() != expected) throw new IllegalStateException("Versiune modificată de altă solicitare; reîncarcă datele.");
        return value;
    }
    private Equivalence requireVersion(Equivalence value, long expected) {
        if (value.version() != expected) throw new IllegalStateException("Versiune modificată de altă solicitare; reîncarcă datele.");
        return value;
    }
    private <E extends Enum<E>> void requireStatus(E actual, E expected) {
        if (actual != expected) throw new IllegalStateException("Operația nu este permisă în starea " + actual + ".");
    }
    private <T> T required(String kind, UUID id, Class<T> type) {
        return store.find(kind, id, type).orElseThrow(() -> notFound("Înregistrarea solicitată nu a fost găsită."));
    }
    private ResponseStatusException notFound(String message) { return new ResponseStatusException(HttpStatus.NOT_FOUND, message); }
}
