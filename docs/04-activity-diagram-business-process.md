# 1.2.2 Business Process Activity Diagram across Bounded Contexts (Figure 2)

**Erasmus Mobility Platform (EMP)**  
**Methodological Alignment:** Course Chapter 2 - Functional Modeling (Alan Dennis et al., UML 2.5 Metamodel) & Project Guidelines (FEAA Master SDBIS / SIA)  
**Visual Artifact:** [`models/diagrams-png/Figura2-Activity-Diagram-Across-Bounded-Contexts.png`](file:///Users/alinprigoreanu/Documents/Object-oriented analysis and design/erasmus-mobility-platform/models/diagrams-png/Figura2-Activity-Diagram-Across-Bounded-Contexts.png)  
**Scalable Vector Graphics (SVG):** [`models/diagrams-png/Figura2-Activity-Diagram-Across-Bounded-Contexts.svg`](file:///Users/alinprigoreanu/Documents/Object-oriented analysis and design/erasmus-mobility-platform/models/diagrams-png/Figura2-Activity-Diagram-Across-Bounded-Contexts.svg)  
**PlantUML Source:** [`docs/diagrams/activity-diagram-erasmus-platform.puml`](file:///Users/alinprigoreanu/Documents/Object-oriented analysis and design/erasmus-mobility-platform/docs/diagrams/activity-diagram-erasmus-platform.puml)

---

## 1. Architectural Partitioning across Swimlanes (Vertical Partitions)

In strict accordance with **Domain-Driven Design (DDD)** and the UML 2.5 metamodel, the macro-level business workflow of the platform is partitioned into **three parallel vertical swimlanes** mapping directly to the three Bounded Contexts:

1. **Swimlane 1 (Left): `Mobility Preparation (Supporting Subdomain)`**  
   * *Operational Responsibility:* Initializes the mobility dossier post-selection, automatically generates onboarding checklist tasks (`ChecklistTask`), tracks administrative readiness (EHIC medical card, OLS linguistic assessment), coordinates Erasmus+ scholarship grant contract execution, and enforces compliance deadlines.
2. **Swimlane 2 (Center): `Equivalence Management (Supporting Subdomain)`**  
   * *Operational Responsibility:* Queries active accredited syllabus equivalence records, compares learning outcomes, and handles missing course exceptions (student proposal $\rightarrow$ academic review $\rightarrow$ ECTS validation $\rightarrow$ institutional catalog registration).
3. **Swimlane 3 (Right): `Learning Agreement Management (Core Domain)`**  
   * *Operational Responsibility:* Governs the authoring and tripartite approval of the study plan (Table A foreign courses mapped to Table B home degree components), enforces the core credit parity invariant ($\sum Table A == \sum Table B \ge 30$ ECTS), manages faculty review, and secures digital institutional confirmation from the host partner across the European EWP network.

---

## 2. Concurrency, Synchronization, and Interruptible Region Semantics

### 2.1 Parallel Synchronization (Fork & Join)
Physical departure preparation requires simultaneous administrative onboarding and academic curriculum planning:
* **Fork Synchronization Bar (Top Black Bar):** Splits the initial control flow into concurrent streams:
  * *Administrative Stream (Swimlane 1):* Progresses through document uploads and scholarship agreements.
  * *Academic Stream (Swimlane 2 $\rightarrow$ Swimlane 3):* Searches equivalences, composes the Learning Agreement, and traverses departmental review.
* **Join Synchronization Bar (Bottom Black Bar):** Blocks final departure readiness until **both** concurrent streams have completed successfully (all mandatory checklist tasks verified AND the Learning Agreement confirmed by the host partner).

### 2.2 Canonical UML 2.5 «InterruptibleActivityRegion» & Interrupting Edge
The concurrent lifecycle between the Fork and Join bars is enclosed within an **`InterruptibleActivityRegion`**:
* **`AcceptEventAction` (Concave Pentagon):** Located in the upper section of the region, `Receive Mobility Cancellation Request (Student / Force Majeure Signal)` possesses no incoming control flow. It remains continuously active throughout the preparation phase.
* **`«interrupting edge»` (Red Dashed Arrow with Lightning Bolt ⚡):** If an abort signal arrives:
  1. Traversal of the interrupting edge **instantly destroys all active parallel tokens** within the region, cleanly halting in-flight tasks in all three swimlanes.
  2. The control flow exits the region boundary and executes the cascading cancellation procedure.

---

## 3. Atomic Cascading Cancellation Flow (Right-Hand Path)

Triggered exclusively by the interrupting edge, this path enforces cross-context consistency and financial accountability:
1. `Cancel Mobility Dossier`: The root mobility record transitions to `CANCELLED`.
2. `Cascade Cancel Learning Agreement`: The `LearningAgreement` aggregate transitions atomically to `CANCELLED`, revoking pending or partial signatures.
3. `Abort Active Checklist Tasks`: Unfinished `ChecklistTask` records are aborted, locking student upload portals.
4. `Publish MobilityCancelledEvent`: The domain event is emitted via the Outbox to notify the host university and European EWP nodes.
5. `Deallocate Erasmus Grant Funds & DRI Reconciliation`: Reserved scholarship budgets are released back into the institutional mobility fund.
6. **Activity Final Node (Bullseye):** The entire process terminates cleanly.

---

## 4. Normal Successful Completion Flow

Upon receiving arrival tokens from both parallel streams at the **Join Bar**:
1. `Validate Complete Mobility Dossier & Issue Departure Certificate`: Verifies 100% compliance across administrative and academic deliverables.
2. `Finalize Mobility Preparation Phase`: Marks the preparation phase as successfully concluded.
3. `Publish MobilityPreparedEvent`: Emits the completion domain event.
4. `Activate "Student Abroad" Academic Status`: The student's academic status is formally updated to active exchange participant.
5. **Activity Final Node (Bullseye):** Successful termination of the onboarding process.

