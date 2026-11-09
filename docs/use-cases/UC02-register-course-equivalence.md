# Use Case Specification: UC02 - Register Academic Equivalence

* **Author:** Bîrgovan A. Mihai-Daniel (Student 2)
* **Subdomain:** Equivalence Management (Supporting Subdomain)
* **Primary Aggregate:** `AcademicEquivalence`
* **Associated Diagram:** Figure 4 (Use Case Diagram), Figure 20 (State Machine), Figure 23 (Sequence Diagram)

---

## 1. Context and Value Proposition

* **Scope:** Erasmus Mobility Platform (EMP) Academic Catalog Module.
* **Goal in Context:** Enable departmental academic evaluators and professors to examine course syllabi pairs between partner institutions, certify curricular parity, establish a validity window, and register the approved equivalence into the searchable institutional catalog.
* **Business Value:** Builds a reusable knowledge bank of certified course equivalences across academic years. Eliminates redundant manual syllabus evaluations and accelerates learning agreement approvals.

---

## 2. Actors and Stakeholders

* **Primary Actor:** `Departmental Evaluator` (professor or academic delegate reviewing syllabus overlap).
* **Secondary Actor:** `Academic Head of Studies` (validates institutional program alignment).
* **Supporting System:** `Learning Agreement Service` (inbound REST client querying active rules).
* **Stakeholders:**
  * Degree Program Committee: Protects degree qualification standards and learning outcomes.
  * Outgoing Exchange Students: Depend on pre-approved equivalences for predictable course selection.
  * Institutional Registrar: Requires authoritative audit trails for diploma supplement credit recognitions.

---

## 3. Preconditions and Postconditions

### 3.1 Preconditions
1. The evaluator holds authenticated credentials with departmental course review permissions.
2. The proposal contains validated course descriptors for both the sending degree program and the receiving institution.
3. The equivalence record exists in status `PROPOSED` or `UNDER_EVALUATION`.

### 3.2 Postconditions
1. The `AcademicEquivalence` aggregate reaches status `ACTIVE`.
2. The record receives an indexed `ValidityWindow` spanning the designated academic terms.
3. The Open Host Service REST API exposes the equivalence for automated remote lookups.
4. An audit log entry records the approving professor ID, timestamp, and certified syllabus checksums.

---

## 4. Invariants and Business Rules (BR)

* **BR-EQ-01 (Curricular Parity Threshold):** Course equivalence approval requires at least 80% topical and competencies overlap between course syllabi (`contentOverlapPercentage >= 80`).
* **BR-EQ-02 (Credit Value Correspondence):** Recognized home credits must equal or exceed host credit ratings for equivalent subject coverage (`recognizedCredits >= hostCourse.credits`).
* **BR-EQ-03 (Validity Window Boundary):** An active equivalence must define explicit `validFrom` and `validUntil` calendar dates. The validity window cannot exceed 3 academic years without re-evaluation.
* **BR-EQ-04 (Bilateral Uniqueness):** Only one active equivalence record may link a specific `(sendCourseCode, hostCourseCode)` pair at any given time.

---

## 5. Main Success Scenario (MSS)

| Step | Initiator | Interaction Description (Active Voice Only) |
| :--- | :--- | :--- |
| 1 | Actor | The evaluator navigates to the Academic Equivalence registration console. |
| 2 | System | The platform presents the evaluation workspace with comparative syllabus views. |
| 3 | Actor | The evaluator enters home course details and corresponding partner university course descriptors. |
| 4 | Actor | The evaluator enters the thematic match breakdown and computed syllabus overlap score. |
| 5 | System | The platform validates that the overlap rating satisfies the statutory threshold (score >= 80%). |
| 6 | Actor | The evaluator defines the validity term (start date and expiration date). |
| 7 | Actor | The evaluator approves the verified equivalence for institutional publication in the academic catalog. |
| 8 | System | The platform verifies the credit correspondence invariant. |
| 9 | System | The platform verifies that no duplicate active equivalence exists for the course pair. |
| 10 | System | The platform transitions aggregate status from `UNDER_EVALUATION` to `APPROVED` and subsequently to `ACTIVE`. |
| 11 | System | The platform indexes the record in the catalog repository and publishes it to the REST API query cache. |
| 12 | System | The platform generates an institutional registration certificate and confirms publication to the evaluator. |

---

## 6. Alternative and Exception Flows

### 4a. Multiple Course Combined Equivalence
* **Condition at Step 4:** Two partner courses together cover the scope of one extensive home subject.
* **4a1:** The evaluator specifies a compound course mapping (Table A lines 1 and 2 map to Table B line 1).
* **4a2:** The platform aggregates ECTS credits across the composite lines.
* **4a3:** The evaluator proceeds to Step 6 with composite recognition rules.

### 5e. Insufficient Curricular Parity
* **Condition at Step 5:** The thematic syllabus overlap measures below 80%.
* **5e1:** The platform rejects the approval action.
* **5e2:** The platform displays the alert: *"Curricular overlap of [X]% does not meet the mandatory 80% threshold. Equivalence cannot be certified in current form."*
* **5e3:** The evaluator chooses either to request additional course syllabus documents from the partner university (returning to `PROPOSED`) or to formally reject the proposal (moving to `RETIRED`).

### 9e. Duplicate Active Rule Collision
* **Condition at Step 9:** An active equivalence already exists for the identical course code pair.
* **9e1:** The platform halts registration.
* **9e2:** The platform displays the existing active record identifier and expiration date.
* **9e3:** The evaluator reviews the existing record to amend its validity window or aborts the duplicate registration.

