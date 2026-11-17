package ro.uaic.feaa.erasmus.api;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import ro.uaic.feaa.erasmus.api.dto.ApiDtos.*;
import ro.uaic.feaa.erasmus.platform.PlatformService;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class PlatformApiIntegrationTest {
    @Autowired MockMvc mvc;
    @Autowired ObjectMapper json;
    @Autowired JdbcTemplate jdbc;
    @Autowired PlatformService platform;

    @BeforeEach void clearDatabase() { jdbc.update("delete from platform_state"); }

    @Test void fullAgreementLifecyclePublishesOutboxAndCompletesExistingChecklist() throws Exception {
        UUID studentId = UUID.randomUUID(), mobilityId = UUID.randomUUID();
        LocalDate start = LocalDate.of(2026, 9, 1), end = LocalDate.of(2027, 1, 31);
        List<CourseLineRequest> home = new ArrayList<>(), host = new ArrayList<>();
        for (int index = 1; index <= 6; index++) {
            UUID lineId = UUID.randomUUID();
            String homeCode = "HOME-" + index, hostCode = "HOST-" + index;
            home.add(new CourseLineRequest(lineId, homeCode, "Curs origine " + index, 5));
            host.add(new CourseLineRequest(lineId, hostCode, "Curs gazdă " + index, 5));
            createActiveEquivalence(homeCode, hostCode, start, end);
        }
        MvcResult created = mvc.perform(post("/api/v1/agreements").contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new CreateAgreementRequest(studentId, mobilityId, "2026-2027", start, end,
                    "Universitatea Gazdă", host, home))))
            .andExpect(status().isCreated()).andExpect(jsonPath("$.status").value("DRAFT"))
            .andExpect(jsonPath("$.version").value(1)).andReturn();
        UUID agreementId = UUID.fromString(json.readTree(created.getResponse().getContentAsString()).get("id").asText());

        MvcResult checklistCreated = mvc.perform(post("/api/v1/mobilities").contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new CreateMobilityRequest(mobilityId, studentId, agreementId))))
            .andExpect(status().isCreated()).andExpect(jsonPath("$.tasks.length()").value(5)).andReturn();
        UUID proofTaskId = UUID.fromString(json.readTree(checklistCreated.getResponse().getContentAsString())
            .get("tasks").get(1).get("id").asText());
        mvc.perform(post("/api/v1/mobilities/{mobilityId}/tasks/{taskId}/proof", mobilityId, proofTaskId)
                .contentType(MediaType.APPLICATION_JSON).content(json.writeValueAsBytes(new ProofRequest("https://example.test/proof/1"))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.tasks[1].status").value("SUBMITTED_FOR_VERIFICATION"));
        mvc.perform(post("/api/v1/mobilities/{mobilityId}/tasks/{taskId}/reject-proof", mobilityId, proofTaskId)
                .contentType(MediaType.APPLICATION_JSON).content(json.writeValueAsBytes(new DecisionRequest(2, "Dovada nu este lizibilă"))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.tasks[1].status").value("PENDING_STUDENT_ACTION"))
            .andExpect(jsonPath("$.tasks[1].reviewNote").value("Dovada nu este lizibilă"));
        mvc.perform(post("/api/v1/mobilities/{mobilityId}/tasks/{taskId}/proof", mobilityId, proofTaskId)
                .contentType(MediaType.APPLICATION_JSON).content(json.writeValueAsBytes(new ProofRequest("https://example.test/proof/2"))))
            .andExpect(status().isOk());
        mvc.perform(post("/api/v1/mobilities/{mobilityId}/tasks/{taskId}/complete", mobilityId, proofTaskId))
            .andExpect(status().isOk()).andExpect(jsonPath("$.tasks[1].status").value("COMPLETED"));
        mvc.perform(post("/api/v1/agreements/{id}/submit", agreementId).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new VersionRequest(1))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("SUBMITTED"));
        mvc.perform(post("/api/v1/agreements/{id}/review", agreementId).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new VersionRequest(2))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("UNDER_REVIEW"));
        mvc.perform(post("/api/v1/agreements/{id}/approve", agreementId).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new ReviewRequest(3, "Compatibilitate verificată"))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("APPROVED_BY_FACULTY"));
        mvc.perform(post("/api/v1/agreements/{id}/host-confirmation", agreementId).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new HostConfirmationRequest(4, "host-signature-42"))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("CONFIRMED_BY_HOST"))
            .andExpect(jsonPath("$.hostEvidenceReference").value("host-signature-42"));

        mvc.perform(post("/api/v1/internal/outbox/process"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.delivered").value(1));
        mvc.perform(get("/api/v1/mobilities/{id}/checklist", mobilityId))
            .andExpect(status().isOk()).andExpect(jsonPath("$.tasks[0].status").value("COMPLETED"))
            .andExpect(jsonPath("$.ready").value(false));
        long versionAfterDelivery = platform.checklist(mobilityId).version();
        mvc.perform(post("/api/v1/internal/outbox/process"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.delivered").value(0));
        org.junit.jupiter.api.Assertions.assertEquals(versionAfterDelivery, platform.checklist(mobilityId).version());
        mvc.perform(get("/api/v1/equivalences/verify").param("homeCode", "HOME-1")
                .param("hostCode", "HOST-1").param("onDate", "2026-10-01"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("ELIGIBLE"));
    }

    @Test void failedSubmissionLeavesDraftUnchangedAndStaleVersionConflicts() throws Exception {
        UUID student = UUID.randomUUID(), mobility = UUID.randomUUID(), line = UUID.randomUUID();
        var home = List.of(new CourseLineRequest(line, "H-1", "Origine", 20));
        var host = List.of(new CourseLineRequest(line, "F-1", "Gazdă", 20));
        MvcResult response = mvc.perform(post("/api/v1/agreements").contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new CreateAgreementRequest(student, mobility, "2026-2027",
                    LocalDate.of(2026, 9, 1), LocalDate.of(2027, 1, 31), "Gazdă", host, home))))
            .andExpect(status().isCreated()).andReturn();
        UUID id = UUID.fromString(json.readTree(response.getResponse().getContentAsString()).get("id").asText());
        var correctedHome = List.of(new CourseLineRequest(line, "H-1", "Origine", 30));
        var correctedHost = List.of(new CourseLineRequest(line, "F-1", "Gazdă", 30));
        mvc.perform(put("/api/v1/agreements/{id}/lines", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new ReplaceLinesRequest(1, correctedHost, correctedHome))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.version").value(2));
        mvc.perform(post("/api/v1/agreements/{id}/submit", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new VersionRequest(2))))
            .andExpect(status().isConflict());
        mvc.perform(get("/api/v1/agreements/{id}", id)).andExpect(status().isOk())
            .andExpect(jsonPath("$.status").value("DRAFT")).andExpect(jsonPath("$.version").value(2));
        mvc.perform(post("/api/v1/agreements/{id}/cancel", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new VersionRequest(99))))
            .andExpect(status().isConflict());
    }

    @Test void equivalencePublicationEnforcesScoreCreditParityAndVersion() throws Exception {
        var request = new CreateEquivalenceRequest("HOME-X", "HOST-X", 5, 5,
            LocalDate.of(2026, 1, 1), LocalDate.of(2027, 12, 31));
        MvcResult created = mvc.perform(post("/api/v1/equivalences").contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(request)))
            .andExpect(status().isCreated()).andExpect(jsonPath("$.status").value("PROPOSED")).andReturn();
        UUID id = UUID.fromString(json.readTree(created.getResponse().getContentAsString()).get("id").asText());
        mvc.perform(post("/api/v1/equivalences/{id}/begin-evaluation", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new VersionRequest(1))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("UNDER_EVALUATION"));
        mvc.perform(post("/api/v1/equivalences/{id}/evaluate-and-publish", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new EvaluationRequest(2, 79, "Scor insuficient"))))
            .andExpect(status().isConflict());
        mvc.perform(get("/api/v1/equivalences")).andExpect(status().isOk())
            .andExpect(jsonPath("$[0].status").value("UNDER_EVALUATION"));
        mvc.perform(post("/api/v1/equivalences/{id}/evaluate-and-publish", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new EvaluationRequest(2, 90, "Conținut și credite compatibile"))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("ACTIVE"));
        mvc.perform(post("/api/v1/equivalences/{id}/retire", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new VersionRequest(3))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("RETIRED"));
    }

    @Test void proposalCanBeExplicitlyRejectedWithReason() throws Exception {
        MvcResult created = mvc.perform(post("/api/v1/equivalences").contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new CreateEquivalenceRequest("HOME-R", "HOST-R", 6, 6,
                    LocalDate.of(2026, 1, 1), LocalDate.of(2027, 12, 31)))))
            .andExpect(status().isCreated()).andReturn();
        UUID id = UUID.fromString(json.readTree(created.getResponse().getContentAsString()).get("id").asText());
        mvc.perform(post("/api/v1/equivalences/{id}/begin-evaluation", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new VersionRequest(1)))).andExpect(status().isOk());
        mvc.perform(post("/api/v1/equivalences/{id}/reject", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new DecisionRequest(2, "Conținut insuficient"))))
            .andExpect(status().isOk()).andExpect(jsonPath("$.status").value("REJECTED"))
            .andExpect(jsonPath("$.rationale").value("Conținut insuficient"));
    }

    @Test void malformedRequestsReturnClientErrorsAndHealthIsAvailable() throws Exception {
        mvc.perform(get("/api/v1/health")).andExpect(status().isOk()).andExpect(jsonPath("$.status").value("UP"));
        mvc.perform(post("/api/v1/equivalences").contentType(MediaType.APPLICATION_JSON).content("{}"))
            .andExpect(status().isBadRequest()).andExpect(jsonPath("$.error").value("validation_failed"));
        mvc.perform(get("/api/v1/agreements/{id}", UUID.randomUUID())).andExpect(status().isNotFound());
    }

    private void createActiveEquivalence(String homeCode, String hostCode, LocalDate start, LocalDate end) throws Exception {
        MvcResult created = mvc.perform(post("/api/v1/equivalences").contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new CreateEquivalenceRequest(homeCode, hostCode, 5, 5, start, end))))
            .andExpect(status().isCreated()).andReturn();
        UUID id = UUID.fromString(json.readTree(created.getResponse().getContentAsString()).get("id").asText());
        mvc.perform(post("/api/v1/equivalences/{id}/begin-evaluation", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new VersionRequest(1)))).andExpect(status().isOk());
        mvc.perform(post("/api/v1/equivalences/{id}/evaluate-and-publish", id).contentType(MediaType.APPLICATION_JSON)
                .content(json.writeValueAsBytes(new EvaluationRequest(2, 90, "Competențe și credite echivalente"))))
            .andExpect(status().isOk());
    }
}
