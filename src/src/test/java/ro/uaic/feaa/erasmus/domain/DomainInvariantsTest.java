package ro.uaic.feaa.erasmus.domain;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import ro.uaic.feaa.erasmus.agreement.domain.*;
import ro.uaic.feaa.erasmus.equivalence.domain.*;
import ro.uaic.feaa.erasmus.preparation.domain.*;
import ro.uaic.feaa.erasmus.shared.*;

import java.time.LocalDate;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("P1 Domain Invariants and Lifecycle Test Suite")
class DomainInvariantsTest {

    @Test
    @DisplayName("LearningAgreement: requires 30 ECTS and credit parity to submit and approve")
    void testLearningAgreementInvariants() {
        AgreementId aid = new AgreementId(UUID.randomUUID());
        StudentId sid = new StudentId(UUID.randomUUID());
        AcademicYear year = new AcademicYear(2026);
        LearningAgreement la = new LearningAgreement(aid, sid, year);

        assertEquals(LearningAgreementStatus.DRAFT, la.status());

        // Cannot submit empty draft (0 credits)
        assertThrows(IllegalStateException.class, la::submit);

        // Add 30 ECTS to Table A and 30 ECTS to Table B
        la.addTableALine(new CourseLineTableA(UUID.randomUUID(), "CS101", "Advanced Algorithms", new ECTSCredits(30)));
        la.addTableBLine(new CourseLineTableB(UUID.randomUUID(), "INFO201", "Algoritmi Avansati", new ECTSCredits(30)));

        assertTrue(la.hasCreditParity());
        assertEquals(30, la.calculateTotalCreditsTableA().value());

        // Submit transitions to SUBMITTED
        la.submit();
        assertEquals(LearningAgreementStatus.SUBMITTED, la.status());

        // Assign coordinator transitions to UNDER_REVIEW
        UUID coordinatorId = UUID.randomUUID();
        la.assignCoordinator(coordinatorId);
        assertEquals(LearningAgreementStatus.UNDER_REVIEW, la.status());

        // Approve generates LearningAgreementApprovedEvent
        LearningAgreementApprovedEvent event = la.approve(coordinatorId);
        assertNotNull(event);
        assertEquals(aid.value(), event.agreementId());
        assertEquals(sid.value(), event.studentId());
        assertEquals(LearningAgreementStatus.APPROVED_BY_FACULTY, la.status());
    }

    @Test
    @DisplayName("AcademicEquivalence: checks validity window and course matching")
    void testAcademicEquivalence() {
        EquivalenceId eid = new EquivalenceId(UUID.randomUUID());
        CourseSyllabus send = new CourseSyllabus(new CourseCode("RO101"), "Sisteme de Operare", new ECTSCredits(6), UUID.randomUUID());
        CourseSyllabus host = new CourseSyllabus(new CourseCode("ES202"), "Operating Systems", new ECTSCredits(6), UUID.randomUUID());
        ValidityWindow window = new ValidityWindow(LocalDate.of(2026, 1, 1), LocalDate.of(2027, 12, 31));

        AcademicEquivalence eq = new AcademicEquivalence(eid, send, host, new ECTSCredits(6), window);
        assertEquals(EquivalenceStatus.PROPOSED, eq.status());
        assertFalse(eq.isCurrentlyValid(LocalDate.of(2026, 6, 1))); // Not ACTIVE yet

        eq.initiateEvaluation();
        assertEquals(EquivalenceStatus.UNDER_EVALUATION, eq.status());

        eq.approve();
        assertEquals(EquivalenceStatus.APPROVED, eq.status());

        eq.activate();
        assertEquals(EquivalenceStatus.ACTIVE, eq.status());
        assertTrue(eq.isCurrentlyValid(LocalDate.of(2026, 6, 1)));
        assertFalse(eq.isCurrentlyValid(LocalDate.of(2028, 1, 1))); // Out of window
    }

    @Test
    @DisplayName("MobilityChecklist: initializes 5 default tasks and tracks completion")
    void testMobilityChecklist() {
        ChecklistId cid = new ChecklistId(UUID.randomUUID());
        StudentId sid = new StudentId(UUID.randomUUID());
        AgreementId aid = new AgreementId(UUID.randomUUID());

        MobilityChecklist checklist = new MobilityChecklist(cid, sid, aid);
        assertEquals(0, checklist.tasks().size());

        checklist.initializeDefaultPreparationTasks();
        assertEquals(5, checklist.tasks().size());
        assertFalse(checklist.areMandatoryTasksComplete());

        // Process tasks
        for (ChecklistTask task : checklist.tasks()) {
            task.attachProof("https://documents.erasmus.uaic.ro/proof/" + task.taskId().value());
            task.markSubmitted();
            checklist.completeTask(task.taskId());
        }

        assertTrue(checklist.areMandatoryTasksComplete());
    }
}
