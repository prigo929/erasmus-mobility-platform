# Strategic Context Map & Ubiquitous Language Glossary

**Erasmus Mobility Platform (EMP)**  
**Methodological Alignment:** Strategic Domain-Driven Design (Eric Evans, Vaughn Vernon) & Model Project Guidelines (FEAA Master SDBIS / SIA)

---

## 1. Strategic Context Map

The strategic architecture decomposes the problem domain into three core operational Bounded Contexts, an integration Shared Kernel, and two supporting generic subdomains:

```mermaid
flowchart TD
    subgraph CoreContext ["Learning Agreement Management (Core Domain)"]
        LA_AR["LearningAgreement (Aggregate Root)"]
        LineA["CourseLineTableA (Internal Entity)"]
        LineB["CourseLineTableB (Internal Entity)"]
    end

    subgraph EquivalenceContext ["Equivalence Management (Supporting Subdomain)"]
        EQ_AR["AcademicEquivalence (Aggregate Root)"]
        Syllabus["CourseSyllabus (Value Object)"]
    end

    subgraph PreparationContext ["Mobility Preparation (Supporting Subdomain)"]
        Checklist_AR["MobilityChecklist (Aggregate Root)"]
        Task_Child["ChecklistTask (Child Entity)"]
    end

    subgraph SharedKernel ["Shared Kernel"]
        SK1["StudentId (Value Object)"]
        SK2["MobilityId (Value Object)"]
        SK3["AcademicPeriod (Value Object)"]
        SK4["ECTSCredits (Value Object)"]
    end

    subgraph GenericContexts ["Generic Subdomains"]
        Notif["Notification Service (Asynchronous Messaging)"]
        Sec["Security & GDPR Audit (RBAC / Append-Only Ledger)"]
    end

    %% Integration Contracts
    CoreContext -->|Uses| SharedKernel
    EquivalenceContext -->|Uses| SharedKernel
    PreparationContext -->|Uses| SharedKernel

    CoreContext -.->|Sync REST Port/Adapter: Search Equivalences| EquivalenceContext
    CoreContext == Transactional Outbox ==>|Async Domain Event: LA Approved / Cancelled| PreparationContext
    PreparationContext -.->|Trigger Alert| Notif
    CoreContext -.->|Trigger Alert| Notif
    CoreContext -.->|Write Audit Trail| Sec
    EquivalenceContext -.->|Write Audit Trail| Sec
```

### Formal Integration Contracts:
1. **Shared Kernel:** The three Bounded Contexts share a minimal set of immutable identity and measurement Value Objects: `StudentId`, `MobilityId`, `AcademicPeriod`, and `ECTSCredits`. Modifications to these types require cross-team consensus.
2. **Customer / Supplier (Synchronous REST with Anti-Corruption Layer):** *Learning Agreement Management* acts as a Customer consuming the course catalog services exposed by *Equivalence Management* (Supplier). Queries pass through a domain Port and an infrastructure REST Adapter to preserve aggregate encapsulation.
3. **Asynchronous Event-Driven Integration (Transactional Outbox Pattern):** Inter-context synchronization between *Learning Agreement* and *Mobility Preparation* is temporal and asynchronous. Upon partner endorsement (`CONFIRMED_BY_HOST`), domain events (`LearningAgreementApprovedEvent`, `LearningAgreementCancelledEvent`) are committed atomically to the local `Outbox` table and delivered via message broker to update onboarding checklist states idempotently.

---

## 2. Ubiquitous Language Glossary

| Term / Concept | Bounded Context | DDD Element / Pattern | Formal Business Role & Architectural Significance |
| :--- | :--- | :--- | :--- |
| **LearningAgreement** | Learning Agreement Management | **Aggregate Root** | The official tripartite legal and academic contract executed between student, home faculty, and partner host institution, establishing pre-approved credit recognition. |
| **CourseLineTableA** | Learning Agreement Management | **Internal Entity** | An educational component at the receiving host institution to be completed abroad, possessing a course code, official title, term, language, and ECTS credits. |
| **CourseLineTableB** | Learning Agreement Management | **Internal Entity** | An accredited educational component from the home degree syllabus that will be replaced and recognized upon passing Table A components. |
| **LearningAgreementStatus** | Learning Agreement Management | **Enum / Value Object** | Contract lifecycle states: `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `APPROVED_BY_FACULTY`, `CONFIRMED_BY_HOST`, `AMENDED`, `CANCELLED`. |
| **AcademicEquivalence** | Equivalence Management | **Aggregate Root** | Institutional mapping binding foreign course syllabi to domestic degree subjects based on verified learning outcomes and credit equivalence. |
| **EquivalenceStatus** | Equivalence Management | **Enum / Value Object** | Equivalence lifecycle states: `PROPOSED`, `UNDER_EVALUATION`, `APPROVED`, `ACTIVE`, `RETIRED`. |
| **MobilityChecklist** | Mobility Preparation | **Aggregate Root** | Central administrative dossier managing the student's preparation checklist and enforcing overall readiness invariants. |
| **ChecklistTask** | Mobility Preparation | **Child Entity** | An atomic unit of administrative onboarding compliance (e.g., EHIC card, grant contract, OLS assessment) encapsulated within MobilityChecklist. |
| **TaskStatus** | Mobility Preparation | **Enum / Value Object** | Task lifecycle states: `INITIALIZED`, `PENDING_STUDENT_ACTION`, `SUBMITTED_FOR_VERIFICATION`, `COMPLETED`, `OVERDUE`, `ABANDONED`. |
| **StudentId** | Shared Kernel | **Value Object** | Globally unique immutable identifier representing the matriculated student across all university subsystems. |
| **MobilityId** | Shared Kernel | **Value Object** | Globally unique immutable identifier representing the academic exchange grant instance. |
| **AcademicPeriod** | Shared Kernel | **Value Object** | Immutable date interval capturing mobility start and end dates, enforcing `endDate >= startDate`. |
| **ECTSCredits** | Shared Kernel | **Value Object** | Decimal numerical value quantifying academic workload according to European Credit Transfer and Accumulation System conventions. |
