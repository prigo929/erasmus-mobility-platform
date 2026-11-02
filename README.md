# Erasmus Mobility Platform (EMP)

An enterprise software architecture and domain model for managing international student exchange programs under the Erasmus+ European framework.

Developed for the **Object-Oriented Analysis and Design (OOAD)** course, Master in Software Development and Business Information Systems (SDBIS / SIA), FEAA, Universitatea „Alexandru Ioan Cuza” din Iași.

---

## 1. Project Overview

The Erasmus Mobility Platform automates the management of international academic exchanges across partner universities. The system replaces fragmented email communications and paper workflows with a distributed, domain-driven architecture. 

The software models three specialized Bounded Contexts:
1. **Learning Agreement Management (Core Domain):** Authoring, tripartite review, and contractual approval of student study plans.
2. **Equivalence Management (Supporting Subdomain):** A verified academic catalog matching home faculty courses with foreign university curricula and validating European Credit Transfer and Accumulation System (ECTS) parity.
3. **Mobility Preparation (Supporting Subdomain):** Administrative task tracking, document checklists, and nomination onboarding.

---

## 2. Team Members and Individual Task Allocation

The project is developed by a team of three students. Individual responsibilities map directly to course deliverables:

### Student 1: Learning Agreement Management (Core Domain)
* **Domain Responsibility:** Core academic workflow, study contracts, and tripartite approvals.
* **Use Case Diagram:** `docs/diagrams/usecase-learning-agreement.puml`
* **Detailed Use Case (SVDPI):** `UC01 - Submit Learning Agreement` (including ECTS balance verification).
* **BDD Specification (Gherkin):** `features/learning-agreement.feature`
* **Dynamic Interaction:** Sequence diagram for study plan submission and academic coordinator review.
* **State Machine:** Entity `LearningAgreement` via `StareLearningAgreement` enum (`DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `APPROVED_BY_FACULTY`, `CONFIRMED_BY_HOST`, `AMENDED`, `CANCELLED`).

### Student 2: Equivalence Management (Supporting Subdomain)
* **Domain Responsibility:** Institutional course catalog, academic syllabus matching, and credit parity rules.
* **Use Case Diagram:** `docs/diagrams/usecase-equivalence-management.puml`
* **Detailed Use Case (SVDPI):** `UC02 - Register Course Equivalence` (including mandatory ECTS range checks).
* **BDD Specification (Gherkin):** `features/equivalence-management.feature`
* **Dynamic Interaction:** Synchronous REST sequence diagram verifying syllabus equivalence queries.
* **State Machine:** Entity `AcademicEquivalence` via `StareEchivalare` enum (`PROPOSED`, `UNDER_EVALUATION`, `APPROVED`, `ACTIVE`, `RETIRED`).

### Student 3: Mobility Preparation (Supporting Subdomain)
* **Domain Responsibility:** Administrative readiness, document onboarding, and deadline enforcement.
* **Use Case Diagram:** `docs/diagrams/usecase-mobility-preparation.puml`
* **Detailed Use Case (SVDPI):** `UC03 - Confirm Nomination` (including automated checklist generation).
* **BDD Specification (Gherkin):** `features/mobility-preparation.feature`
* **Dynamic Interaction:** Asynchronous sequence diagram using Transactional Outbox for nomination events.
* **State Machine:** Entity `ChecklistTask` via `StareSarcina` enum (`INITIALIZED`, `PENDING_STUDENT_ACTION`, `SUBMITTED_FOR_VERIFICATION`, `COMPLETED`, `OVERDUE`).
* **Part II Lead (Design Patterns):** Strategy, Factory, Singleton, and Facade implementation for variable scholarship grants or equivalence evaluation engines.

---

## 3. Team Deliverables

* **Domain Specification:** Comprehensive narrative detailing subdomains, transactions, and business invariants (`docs/01-subdomains-and-transactions.md`).
* **Non-Functional Requirements:** SLA matrix containing measured latency, throughput, and audit boundaries (`docs/02-nfr-matrix.md`).
* **Strategic Context Map:** Upstream/Downstream contracts, Shared Kernel, and Open Host Services (`docs/03-context-map-glossary.md`).
* **Cross-Context Activity Diagram:** End-to-end business process covering all three Bounded Contexts with vertical swimlanes, parallel forks, and an interruptible cancellation region.
* **Layered Class Models (Figures 8-15):** Presentation, Application, Domain, and Infrastructure layers using Enterprise Architect.

---

## 4. Repository Structure

```text
erasmus-mobility-platform/
│
├── .gitignore                          # Excludes EA SQLite locks (~$*.qea) and build artifacts
├── README.md                           # Team roles, deliverable mapping, and project setup
│
├── docs/                               # Analysis, architecture memos, and specifications
│   ├── 01-subdomains-and-transactions.md # 3-page problem statement and transaction breakdown
│   ├── 02-nfr-matrix.md                # Measurable quality attributes and SLA targets
│   ├── 03-context-map-glossary.md      # Ubiquitous language and integration contracts
│   └── use-cases/                      # Narrative SVDPI use case specifications
│       ├── UC01-submit-learning-agreement.md
│       ├── UC02-register-course-equivalence.md
│       └── UC03-confirm-nomination.md
│
├── features/                           # Gherkin BDD living documentation (.feature files)
│   ├── learning-agreement.feature
│   ├── equivalence-management.feature
│   └── mobility-preparation.feature
│
├── models/                             # Enterprise Architect models and exports
│   ├── EA-Repository/
│   │   └── ErasmusModel.qea            # Master SQLite repository for Enterprise Architect v16+
│   ├── xmi-exports/                    # XMI / Native XML schema packages for version control
│   └── diagrams-png/                   # Exported diagrams for documentation
│
└── src/                                # Reference implementation (JDK 23 / Spring Boot)
    ├── pom.xml
    └── src/main/java/ro/uaic/feaa/erasmus/
        ├── shared/                     # Shared Kernel (StudentId, MobilityId, AcademicPeriod)
        ├── agreement/                  # Core Domain: Learning Agreement Aggregate
        ├── equivalence/                # Supporting Domain: Equivalence Aggregate
        ├── preparation/                # Supporting Domain: Checklist Aggregate
        └── patterns/                   # GoF & GRASP refactoring (Strategy, Factory, Singleton, Facade)
```


## 5. Development and Tooling Requirements

* **Enterprise Architect v16+:** Core UML CASE tool (.qea SQLite file format). Always close the tool before committing to release the database lock file.
* **Java Development Kit (JDK) 23:** Modern Java baseline utilizing records, sealed interfaces, and pattern matching.
* **IntelliJ IDEA (2024.3+):** Recommended IDE for source inspection, unit testing, and pattern validation.
* **Maven 3.9+:** Project build management and dependency resolution.

```bash
# Verify build and run architecture constraint checks
cd src
mvn clean test
