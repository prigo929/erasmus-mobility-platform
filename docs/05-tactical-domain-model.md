# Chapter 2. Tactical Domain-Driven Design Model (Figure 8)

**Erasmus Mobility Platform (EMP)**  
**Methodological Alignment:** Strategic & Tactical DDD (Eric Evans, Vaughn Vernon) and Course Structural Modeling (FEAA Master SDBIS / SIA)  
**Visual Artifact:** [`models/diagrams-png/Figura8-Tactical-DDD-Domain-Model.png`](file:///Users/alinprigoreanu/Documents/Object-oriented analysis and design/erasmus-mobility-platform/models/diagrams-png/Figura8-Tactical-DDD-Domain-Model.png)  
**Scalable Vector Graphics (SVG):** [`models/diagrams-png/Figura8-Tactical-DDD-Domain-Model.svg`](file:///Users/alinprigoreanu/Documents/Object-oriented analysis and design/erasmus-mobility-platform/models/diagrams-png/Figura8-Tactical-DDD-Domain-Model.svg)  
**PlantUML Source:** [`docs/diagrams/fig8-tactical-domain-model.puml`](file:///Users/alinprigoreanu/Documents/Object-oriented analysis and design/erasmus-mobility-platform/docs/diagrams/fig8-tactical-domain-model.puml)

---

## 1. Tactical Patterns and Consistency Boundaries

Up to this point, the analysis focused on the functional perspective. We now shift to the structural perspective. We apply Tactical Domain-Driven Design (DDD) to enforce consistency boundaries and protect transactional invariants across the three subdomains.

In DDD, the domain model does not serve query projection workloads. It serves command processing and business rule enforcement.

The tactical patterns applied include:
* **Aggregate Root (`«Aggregate Root»`):** The primary entry point for modifying business state. External classes never hold persistent references to internal child entities.
* **Internal Entity (`«Entity»`):** Objects with explicit identity whose state mutates over time, accessible only through their owning Aggregate Root.
* **Value Object (`«Value Object»`):** Immutable concepts defined entirely by their attributes without independent identity. They contain zero setter methods.
* **Domain Service (`«Domain Service»`):** Stateless operations implementing calculations or multi-entity comparisons that do not belong to a single entity.
* **Shared Kernel:** Common identity types shared across Bounded Context boundaries to correlate records without tight structural coupling.

---

## 2. Table 2.1 Transactional Invariants Matrix for the Core Aggregate

| Business Invariant Rule | Guaranteed by Aggregate Root Method | Failure Mode if Aggregate Root is Bypassed |
| :--- | :--- | :--- |
| **ECTS Parity Invariant:** Cumulative credits in Table A must strictly equal Table B and meet the minimum threshold ($\sum A = \sum B \ge 30.00$ ECTS per semester). | `LearningAgreement.validateEctsBalance()` | A student modifies course lines directly in the database, creating a contract with credit deficits that the faculty cannot legally graduate. |
| **Atomic Cascading Cancellation:** Cancelling a mobility contract marks the agreement as `CANCELLED` and cascades through child lines atomically. | `LearningAgreement.cancel()` | A cancelled exchange program leaves active course lines in registration tables, causing unauthorized grade requests from host institutions. |
| **Submissions Lock Mutation:** Transitioning from `DRAFT` to `SUBMITTED` locks course line collections against direct client edits. | `LearningAgreement.submit()` | A student swaps difficult courses for unapproved electives while the coordinator is reviewing the contract. |
| **Tripartite Endorsement Sequence:** Partner confirmation (`CONFIRMED_BY_HOST`) is illegal unless faculty approval (`APPROVED_BY_FACULTY`) has occurred. | `LearningAgreement.confirmByHost()` | An unvetted curriculum receives foreign endorsement without faculty oversight, triggering institutional liability. |

---

## 3. Structural Decomposition across Contexts

### 3.1 Common Types (Shared Kernel)
The Shared Kernel encapsulates four immutable Value Objects:
1. `StudentId`: UUID wrapper enforcing non-null university matriculation identity.
2. `MobilityId`: UUID wrapper identifying the specific exchange allocation dossier.
3. `AcademicPeriod`: Encapsulates `startDate` and `endDate`, strictly validating `endDate >= startDate`.
4. `ECTSCredits`: Encapsulates a positive decimal `BigDecimal`, preventing negative or zero credit allocations.

### 3.2 Learning Agreement Management (Core Domain)
The core package isolates the contract aggregate:
* **`LearningAgreement` (Aggregate Root):** Enforces credit parity and orchestrates approvals. Holds private collections of Table A and Table B lines.
* **`CourseLineTableA` and `CourseLineTableB` (Internal Entities):** Maintain line items for host and home courses. Their lifespan is bound to the parent agreement via strict UML composition (`1` to `1..*`). Deleting the agreement destroys all internal lines.
* **`ECTSParityService` (Domain Service):** Stateless calculator verifying credit totals across foreign and domestic tables.
* **`LearningAgreementStatus` (Enum):** Governs lifecycle transitions (`DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `APPROVED_BY_FACULTY`, `CONFIRMED_BY_HOST`, `AMENDED`, `CANCELLED`).

### 3.3 Equivalence Management (Supporting Subdomain)
* **`AcademicEquivalence` (Aggregate Root):** Maintains the canonical link between a host course syllabus and a domestic subject.
* **`CourseSyllabus` (Value Object):** Immutable record capturing learning outcomes, contact hours, and grading rubrics.
* **`SyllabusEvaluationService` (Domain Service):** Computes text and credit similarity metrics between two course syllabi.
* **`EquivalenceStatus` (Enum):** Lifecycle states (`PROPOSED`, `UNDER_EVALUATION`, `APPROVED`, `ACTIVE`, `RETIRED`).

### 3.4 Mobility Preparation (Supporting Subdomain)
* **`MobilityDossier` (Aggregate Root):** Oversees the student exchange record, tracking target destinations and scholarship funding.
* **`ChecklistTask` (Aggregate Root):** Discrete administrative compliance task enforcing verification deadlines.
* **`DocumentAttachment` (Value Object):** Stores file names, SHA-256 cryptographic hashes, and cloud storage references.
* **`GrantAmount` (Value Object):** Immutable currency and financial calculation model.
* **`TaskStatus` and `MobilityStatus` (Enums):** Lifecycle states for onboarding milestones and student mobility stages.
