package ro.uaic.feaa.erasmus.api.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;
import ro.uaic.feaa.erasmus.platform.PlatformState;

public final class ApiDtos {
    private ApiDtos() {}
    public record CourseLineRequest(@NotNull UUID lineId, @NotBlank String code, @NotBlank String title,
                                    @Min(1) int credits) {}
    public record CreateAgreementRequest(@NotNull UUID studentId, @NotNull UUID mobilityId,
        @NotBlank String academicYear, @NotNull LocalDate periodStart, @NotNull LocalDate periodEnd,
        @NotBlank String hostUniversity, @NotEmpty List<@Valid CourseLineRequest> tableA,
        @NotEmpty List<@Valid CourseLineRequest> tableB) {}
    public record VersionRequest(@Min(1) long expectedVersion) {}
    public record ReplaceLinesRequest(@Min(1) long expectedVersion,
        @NotEmpty List<@Valid CourseLineRequest> tableA, @NotEmpty List<@Valid CourseLineRequest> tableB) {}
    public record ReviewRequest(@Min(1) long expectedVersion, String reason) {}
    public record DecisionRequest(@Min(1) long expectedVersion, @NotBlank String reason) {}
    public record HostConfirmationRequest(@Min(1) long expectedVersion, @NotBlank String evidenceReference) {}
    public record CreateEquivalenceRequest(@NotBlank String homeCode, @NotBlank String hostCode,
        @Min(1) int homeCredits, @Min(1) int hostCredits,
        @NotNull LocalDate validFrom, @NotNull LocalDate validTo) {}
    public record EvaluationRequest(@Min(1) long expectedVersion, @Min(0) @Max(100) int score,
                                    @NotBlank String rationale) {}
    public record CreateMobilityRequest(@NotNull UUID mobilityId, @NotNull UUID studentId,
                                        @NotNull UUID agreementId) {}
    public record ProofRequest(@NotBlank String proofUri) {}
    public record EventRequest(@NotNull UUID eventId, @NotBlank String type, @Min(1) long sourceVersion) {}
    public record VerificationResponse(String status, String message) {}
    public record CourseLineResponse(UUID lineId, String code, String title, int credits) {}
    public record AgreementResponse(UUID id, UUID studentId, UUID mobilityId, String academicYear,
        LocalDate periodStart, LocalDate periodEnd, String hostUniversity,
        List<CourseLineResponse> tableA, List<CourseLineResponse> tableB,
        PlatformState.AgreementStatus status, String lastDecisionReason,
        String hostEvidenceReference, long version) {}
    public record EquivalenceResponse(UUID id, String homeCode, String hostCode, int homeCredits,
        int hostCredits, LocalDate validFrom, LocalDate validTo,
        PlatformState.EquivalenceStatus status, Integer score, String rationale, long version) {}
    public record TaskResponse(UUID id, PlatformState.TaskType type, PlatformState.TaskStatus status,
                               LocalDate deadline, String proofUri, String reviewNote) {}
    public record ChecklistResponse(UUID mobilityId, UUID studentId, UUID agreementId,
        List<TaskResponse> tasks, boolean cancelled, boolean ready, long version) {}
}
