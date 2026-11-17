package ro.uaic.feaa.erasmus.api;

import jakarta.validation.Valid;
import java.net.URI;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import ro.uaic.feaa.erasmus.api.dto.ApiDtos.*;
import ro.uaic.feaa.erasmus.platform.PlatformService;
import ro.uaic.feaa.erasmus.platform.PlatformState.*;

@RestController
@RequestMapping("/api/v1")
public class PlatformApiController {
    private final PlatformService platform;
    public PlatformApiController(PlatformService platform) { this.platform = platform; }

    @GetMapping("/health")
    public HealthResponse health() { return new HealthResponse("UP", "Erasmus Mobility Platform API"); }
    public record HealthResponse(String status, String service) {}

    @PostMapping("/agreements")
    public ResponseEntity<AgreementResponse> createAgreement(@Valid @RequestBody CreateAgreementRequest request) {
        Agreement created = platform.createAgreement(request);
        return ResponseEntity.created(URI.create("/api/v1/agreements/" + created.id())).body(agreementDto(created));
    }
    @GetMapping("/agreements/{id}")
    public AgreementResponse getAgreement(@PathVariable UUID id) { return agreementDto(platform.getAgreement(id)); }
    @PutMapping("/agreements/{id}/lines")
    public AgreementResponse replaceLines(@PathVariable UUID id, @Valid @RequestBody ReplaceLinesRequest request) {
        return agreementDto(platform.replaceAgreementLines(id, request));
    }
    @PostMapping("/agreements/{id}/submit")
    public AgreementResponse submit(@PathVariable UUID id, @Valid @RequestBody VersionRequest request) { return agreementDto(platform.submitAgreement(id, request)); }
    @PostMapping("/agreements/{id}/review")
    public AgreementResponse review(@PathVariable UUID id, @Valid @RequestBody VersionRequest request) { return agreementDto(platform.beginReview(id, request)); }
    @PostMapping("/agreements/{id}/approve")
    public AgreementResponse approve(@PathVariable UUID id, @Valid @RequestBody ReviewRequest request) { return agreementDto(platform.approve(id, request)); }
    @PostMapping("/agreements/{id}/request-changes")
    public AgreementResponse requestChanges(@PathVariable UUID id, @Valid @RequestBody DecisionRequest request) { return agreementDto(platform.requestChanges(id, request)); }
    @PostMapping("/agreements/{id}/host-confirmation")
    public AgreementResponse confirmHost(@PathVariable UUID id, @Valid @RequestBody HostConfirmationRequest request) { return agreementDto(platform.confirmHost(id, request)); }
    @PostMapping("/agreements/{id}/cancel")
    public AgreementResponse cancel(@PathVariable UUID id, @Valid @RequestBody VersionRequest request) { return agreementDto(platform.cancel(id, request)); }

    @PostMapping("/equivalences")
    public ResponseEntity<EquivalenceResponse> propose(@Valid @RequestBody CreateEquivalenceRequest request) {
        Equivalence created = platform.propose(request);
        return ResponseEntity.created(URI.create("/api/v1/equivalences/" + created.id())).body(equivalenceDto(created));
    }
    @GetMapping("/equivalences")
    public List<EquivalenceResponse> equivalences() { return platform.equivalences().stream().map(this::equivalenceDto).toList(); }
    @GetMapping("/equivalences/{id}")
    public EquivalenceResponse equivalence(@PathVariable UUID id) { return equivalenceDto(platform.getEquivalence(id)); }
    @PostMapping("/equivalences/{id}/begin-evaluation")
    public EquivalenceResponse beginEvaluation(@PathVariable UUID id, @Valid @RequestBody VersionRequest request) { return equivalenceDto(platform.beginEvaluation(id, request)); }
    @PostMapping("/equivalences/{id}/evaluate-and-publish")
    public EquivalenceResponse evaluateAndPublish(@PathVariable UUID id, @Valid @RequestBody EvaluationRequest request) { return equivalenceDto(platform.evaluateAndPublish(id, request)); }
    @PostMapping("/equivalences/{id}/reject")
    public EquivalenceResponse rejectEquivalence(@PathVariable UUID id, @Valid @RequestBody DecisionRequest request) { return equivalenceDto(platform.rejectEquivalence(id, request)); }
    @PostMapping("/equivalences/{id}/retire")
    public EquivalenceResponse retireEquivalence(@PathVariable UUID id, @Valid @RequestBody VersionRequest request) { return equivalenceDto(platform.retireEquivalence(id, request)); }
    @GetMapping("/equivalences/verify")
    public VerificationResponse verify(@RequestParam String homeCode, @RequestParam String hostCode,
                                       @RequestParam LocalDate onDate) { return platform.verify(homeCode, hostCode, onDate); }

    @PostMapping("/mobilities")
    public ResponseEntity<ChecklistResponse> createChecklist(@Valid @RequestBody CreateMobilityRequest request) {
        Checklist created = platform.createChecklist(request);
        return ResponseEntity.created(URI.create("/api/v1/mobilities/" + created.mobilityId() + "/checklist")).body(checklistDto(created));
    }
    @GetMapping("/mobilities/{mobilityId}/checklist")
    public ChecklistResponse checklist(@PathVariable UUID mobilityId) { return checklistDto(platform.checklist(mobilityId)); }
    @PostMapping("/mobilities/{mobilityId}/tasks/{taskId}/proof")
    public ChecklistResponse submitProof(@PathVariable UUID mobilityId, @PathVariable UUID taskId,
                                 @Valid @RequestBody ProofRequest request) { return checklistDto(platform.submitProof(mobilityId, taskId, request)); }
    @PostMapping("/mobilities/{mobilityId}/tasks/{taskId}/complete")
    public ChecklistResponse completeTask(@PathVariable UUID mobilityId, @PathVariable UUID taskId) { return checklistDto(platform.completeTask(mobilityId, taskId)); }
    @PostMapping("/mobilities/{mobilityId}/tasks/{taskId}/reject-proof")
    public ChecklistResponse rejectTaskProof(@PathVariable UUID mobilityId, @PathVariable UUID taskId,
                                              @Valid @RequestBody DecisionRequest request) { return checklistDto(platform.rejectTaskProof(mobilityId, taskId, request)); }
    @PostMapping("/internal/outbox/process")
    public OutboxProcessResponse processOutbox() { return new OutboxProcessResponse(platform.processOutbox(), platform.pendingOutboxCount()); }
    public record OutboxProcessResponse(int delivered, long pending) {}

    private AgreementResponse agreementDto(Agreement value) {
        return new AgreementResponse(value.id(), value.studentId(), value.mobilityId(), value.academicYear(),
            value.periodStart(), value.periodEnd(), value.hostUniversity(),
            value.tableA().stream().map(line -> new CourseLineResponse(line.lineId(), line.code(), line.title(), line.credits())).toList(),
            value.tableB().stream().map(line -> new CourseLineResponse(line.lineId(), line.code(), line.title(), line.credits())).toList(),
            value.status(), value.lastDecisionReason(), value.hostEvidenceReference(), value.version());
    }
    private EquivalenceResponse equivalenceDto(Equivalence value) {
        return new EquivalenceResponse(value.id(), value.homeCode(), value.hostCode(), value.homeCredits(), value.hostCredits(),
            value.validFrom(), value.validTo(), value.status(), value.score(), value.rationale(), value.version());
    }
    private ChecklistResponse checklistDto(Checklist value) {
        return new ChecklistResponse(value.mobilityId(), value.studentId(), value.agreementId(),
            value.tasks().stream().map(task -> new TaskResponse(task.id(), task.type(), task.status(), task.deadline(), task.proofUri(), task.reviewNote())).toList(),
            value.cancelled(), !value.cancelled() && !value.tasks().isEmpty() && value.tasks().stream().allMatch(task -> task.status() == TaskStatus.COMPLETED), value.version());
    }
}
