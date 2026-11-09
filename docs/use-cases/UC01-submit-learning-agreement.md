# Use Case Specification: UC01 - Submit Learning Agreement

* **Author:** Prigoreanu Alin-Gabriel (Student 1)
* **Subdomain:** Learning Agreement Management (Core Domain)
* **Primary Aggregate:** `LearningAgreement`
* **Associated Diagram:** Figure 3 (Use Case Diagram), Figure 19 (State Machine), Figure 22 (Sequence Diagram)

---

## 1. Context and Value Proposition

* **Scope:** Erasmus Mobility Platform (EMP) Academic Module.
* **Goal in Context:** Allow an outgoing exchange student to assemble study course pairs across host and home curriculums, verify their academic equivalence against institutional catalogs, and formally submit the agreement for faculty review.
* **Business Value:** Guarantees that outgoing students submit credit-compliant learning contracts before departure, preventing credit loss upon return and ensuring alignment with European Commission EWP standards.

---

## 2. Actors and Stakeholders

* **Primary Actor:** `Outgoing Student` (initiates agreement drafting, enters courses, submits contract).
* **Secondary Actor:** `Faculty Coordinator` (evaluates submitted contracts, requests revisions, grants institutional approval).
* **Supporting System:** `Equivalence Management Service` (remote catalog accessed synchronously via REST).
* **Stakeholders:**
  * Home Faculty Department: Requires that incoming recognition matches degree program requirements.
  * Receiving Host Institution: Requires bilateral course transparency.
  * Department of International Relations (DRI): Monitors institutional compliance.

---

## 3. Preconditions and Postconditions

### 3.1 Preconditions
1. The student holds an active exchange nomination for an approved bilateral partner institution.
2. The current academic term permits contract submissions according to faculty calendar windows.
3. The student has opened a draft learning agreement in status `DRAFT`.

### 3.2 Postconditions
1. The `LearningAgreement` aggregate transitions to status `SUBMITTED`.
2. The course lines in Table A and Table B become immutable for student editing.
3. The agreement enters the review queue of the appointed departmental faculty coordinator.
4. An automated confirmation email reaches the student inbox with the timestamped submission manifest.

---

## 4. Invariants and Business Rules (BR)

* **BR-LA-01 (Credit Volume Invariant):** The total ECTS credits in Table A must be greater than or equal to 30.0 credits for a single semester exchange (or 60.0 for a full academic year).
* **BR-LA-02 (Credit Parity Invariant):** The sum of recognized home credits in Table B must exactly match the sum of completed host credits in Table A (`sum(TableA.credits) == sum(TableB.credits)`).
* **BR-LA-03 (Course Line Association):** Every course line in Table A must map to at least one valid recognition counterpart in Table B. Orphaned course lines are rejected.
* **BR-LA-04 (Submission Immutability):** Once submitted, neither Table A nor Table B can be modified without a formal rejection or coordinator-requested revision.

---

## 5. Main Success Scenario (MSS)

| Step | Initiator | Interaction Description (Active Voice Only) |
| :--- | :--- | :--- |
| 1 | Actor | The student opens the Learning Agreement drafting dashboard. |
| 2 | System | The platform displays the current draft containing Table A and Table B course line grids. |
| 3 | Actor | The student enters course codes, titles, and ECTS credit values for host subjects (Table A). |
| 4 | Actor | The student selects corresponding home university degree courses for academic recognition (Table B). |
| 5 | Actor | The student triggers the "Verify Equivalences" action. |
| 6 | System | The platform queries the Equivalence Management catalog via REST adapter and displays verified credit matches. |
| 7 | Actor | The student reviews the verified course pairs and submits the draft learning agreement to the platform for institutional review. |
| 8 | System | The platform verifies the credit volume invariant (total ECTS >= 30.0 credits). |
| 9 | System | The platform verifies the credit parity invariant (`sum(TableA) == sum(TableB)`). |
| 10 | System | The platform transitions the agreement status from `DRAFT` to `SUBMITTED`. |
| 11 | System | The platform locks all course rows against further edits. |
| 12 | System | The platform assigns the contract to the faculty coordinator and displays a submission receipt to the student. |

---

## 6. Alternative and Exception Flows

### 6a. Course Equivalences Pending in Catalog
* **Condition at Step 6:** One or more course pairs do not exist in the active equivalence catalog.
* **6a1:** The platform displays an advisory banner indicating that unverified courses will require manual coordinator syllabus assessment.
* **6a2:** The student confirms intent to submit unlisted courses with attached syllabus URLs.
* **6a3:** The system records the syllabus attachments and allows the student to proceed to Step 7.

### 8e. Total Credits Under Statutory Threshold
* **Condition at Step 8:** The aggregate calculates total host credits strictly below 30.0 ECTS.
* **8e1:** The platform rejects the submission request.
* **8e2:** The platform highlights Table A with the message: *"Minimum semester requirement is 30.0 ECTS. Current total is [X] ECTS."*
* **8e3:** The agreement remains in status `DRAFT`.
* **8e4:** The student returns to Step 3 to add complementary course selections.

### 9e. Credit Parity Discrepancy
* **Condition at Step 9:** The credit sum of Table A does not equal the credit sum of Table B.
* **9e1:** The platform blocks the transition and flags mismatched course mappings.
* **9e2:** The platform displays the error: *"Table A sum ([X] ECTS) does not equal Table B sum ([Y] ECTS). Balance course recognition before submitting."*
* **9e3:** The aggregate preserves state `DRAFT`. The student returns to Step 4 to balance course credit assignments.

