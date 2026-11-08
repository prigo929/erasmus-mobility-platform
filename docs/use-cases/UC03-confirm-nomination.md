# Use Case Specification: UC03 - Confirm Nomination

* **Author:** Schipor Ana-Maria (Student 3)
* **Subdomain:** Mobility Preparation (Supporting Subdomain)
* **Primary Aggregate:** `MobilityChecklist`
* **Associated Diagram:** Figure 5 (Use Case Diagram), Figure 21 (State Machine), Figure 25 (Sequence Diagram)

---

## 1. Context and Value Proposition

* **Scope:** Erasmus Mobility Platform (EMP) Student Onboarding and Compliance Module.
* **Goal in Context:** Process an inbound institutional nomination or approved agreement, create a student compliance dossier with personalized preparation tasks, receive verified document proofs (grant agreements, insurance certificates), and confirm student departure readiness.
* **Business Value:** Guarantees that outgoing students satisfy all legal, medical, and financial regulations before travelling abroad. Protects the university from liability and ensures compliance with Erasmus+ grant disbursement conditions.

---

## 2. Actors and Stakeholders

* **Primary Actor:** `Mobility Officer` (verifies uploaded documents, confirms nomination readiness).
* **Secondary Actor:** `Nominated Student` (uploads required proofs, signs grant agreements).
* **Supporting System:** `Message Broker (RabbitMQ)` (delivers asynchronous nomination and approval events).
* **Stakeholders:**
  * Erasmus Institutional Office: Oversees student welfare and international travel authorizations.
  * Faculty Dean's Office: Requires confirmation that nominated students maintain active enrollment.
  * National Agency: Audits grant allocations against verified mobility files.

---

## 3. Preconditions and Postconditions

### 3.1 Preconditions
1. The student holds an approved nomination from the selection committee.
2. The Learning Agreement context has published an approved contract event over the message broker.
3. The Mobility Preparation message receiver has ingested the event and verified idempotency.

### 3.2 Postconditions
1. The `MobilityChecklist` aggregate holds verified completions for all mandatory tasks.
2. The checklist status marks the student as `READY_FOR_DEPARTURE`.
3. The platform unlocks the first installment of the Erasmus+ financial grant.
4. An official nomination confirmation package reaches the partner university international office.

---

## 4. Invariants and Business Rules (BR)

* **BR-MP-01 (Mandatory Task Set Invariant):** Every student checklist must contain at least three non-waivable tasks:
  1. Signed Erasmus+ Grant Agreement.
  2. Valid European Health Insurance Card (EHIC) or equivalent private coverage.
  3. Official Acceptance Letter from the host institution.
* **BR-MP-02 (Departure Readiness Gate):** The platform strictly prohibits confirming nomination departure readiness while any mandatory task remains in status `INITIALIZED`, `PENDING_STUDENT_ACTION`, `SUBMITTED_FOR_VERIFICATION`, or `OVERDUE`.
* **BR-MP-03 (Idempotent Nomination Processing):** An incoming event with identifier `eventId` can generate at most one preparation checklist. Duplicate broker redeliveries must terminate without creating redundant records.
* **BR-MP-04 (Document File Integrity):** Uploaded proof attachments must be verified PDF documents with cryptographic integrity hashes stored in the audit ledger.

---

## 5. Main Success Scenario (MSS)

| Step | Initiator | Interaction Description (Active Voice Only) |
| :--- | :--- | :--- |
| 1 | System | The RabbitMQ listener receives an inbound `LearningAgreementApprovedEvent` payload. |
| 2 | System | The platform queries the idempotency port and confirms the event is unhandled. |
| 3 | System | The platform instantiates a `MobilityChecklist` aggregate and populates default compliance tasks. |
| 4 | System | The platform dispatches an onboarding email with task deadlines to the student. |
| 5 | Actor | The student accesses the preparation portal and uploads the signed grant agreement and insurance proof. |
| 6 | System | The platform stores the document references and transitions the tasks to `SUBMITTED_FOR_VERIFICATION`. |
| 7 | Actor | The mobility officer opens the verification dashboard and inspects the attached document proofs. |
| 8 | Actor | The mobility officer approves each submitted proof. |
| 9 | System | The platform transitions all task statuses to `COMPLETED`. |
| 10 | System | The platform evaluates the departure readiness invariant (`areMandatoryTasksComplete()`). |
| 11 | System | The platform transitions checklist status to `CONFIRMED_READY_FOR_DEPARTURE`. |
| 12 | System | The platform triggers grant payment authorization and transmits departure confirmation to the student. |

---

## 6. Alternative and Exception Flows

### 5a. Student Requests Task Waiver for Private Insurance
* **Condition at Step 5:** The student holds alternative international insurance not covered by EHIC.
* **5a1:** The student uploads an private insurance policy with an exemption request.
* **5a2:** The mobility officer reviews the policy coverage limits against institutional liability minimums.
* **5a3:** The officer approves the alternative proof with a waiver annotation and proceeds to Step 8.

### 8e. Rejected Document Proof
* **Condition at Step 8:** An uploaded document is expired, incomplete, or illegible.
* **8e1:** The mobility officer rejects the submission and inputs feedback notes.
* **8e2:** The platform reverts the specific task to `PENDING_STUDENT_ACTION`.
* **8e3:** The platform sends an urgent rejection notification to the student with instructions to resubmit.
* **8e4:** The departure gate remains locked. Execution loops back to Step 5.

### 2e. Duplicate Event Ingestion
* **Condition at Step 2:** The event ID already exists in the `processed_events` table.
* **2e1:** The application service flags a duplicate event redelivery.
* **2e2:** The platform logs an idempotency notice and skips aggregate instantiation.
* **2e3:** The message receiver transmits an AMQP acknowledgment (`basicAck`) to RabbitMQ to clear the redundant message.

