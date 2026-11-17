# Erasmus Mobility Platform (EMP)

## Modificări față de originalul din Git

Am comparat fișierele din IDE cu originalul din Git. Auditul cerințelor nu a adăugat modificări. Diferențele existente sunt:

### Texte

- **README.md:** UC03 apare acum ca „Apply Agreement Event to Mobility Checklist”, în loc de „Confirm Nomination”.
- **docs/01-subdomains-and-transactions.md:** am restrâns scopul la o mobilitate de un semestru și am scos din fluxul descris integrarea EWP, plata bursei, revizuirile cu termen de 5 zile și amendamentele din timpul mobilității. Am schimbat echivalențele din 1:1 sau N:M în 1:1 și am înlocuit prezentarea veche T1–T5 cu fluxul din Figura 2.
- **docs/11-state-machines.md:** am rescris descrierile pentru Figures 19–21 ca să corespundă stărilor și tranzițiilor din diagrame: fără `AMENDED` pentru acord, fără `APPROVED` intermediar pentru echivalență și cu anularea sarcinilor active la retragere.
- **docs/12-sequence-diagrams.md:** descrierile Figures 22–25 explică acum UC01 submitere, UC02 evaluare/publicare, confirmarea gazdei prin outbox și aplicarea evenimentului la checklistul existent.
- **UC01:** am înlocuit descrierea veche cu pași pentru verificarea fiecărei mapări, regulile 1:1 și ECTS, rezultate `INELIGIBLE`/`UNAVAILABLE` și salvarea versiunii `SUBMITTED`.
- **UC02:** am înlocuit fluxul vechi cu evaluare și publicare într-o singură operație, scorul proiectului de 80/100, credite egale, perioadă validă, unicitate și respingere separată.
- **UC03:** l-am schimbat din confirmarea nominalizării și inițializarea checklistului în aplicarea evenimentului de confirmare/anulare la checklistul existent.
- **Cele trei fișiere `.feature`:** scenariile vechi au fost înlocuite cu scenarii care urmează aceste UC-uri: erori și conflicte de versiune pentru UC01, publicare/respingere/conflicte pentru UC02, deduplicare și evenimente vechi pentru UC03.

### Diagrame

Sursele PlantUML și exporturile PNG/SVG au fost schimbate pentru Figures 2, 8–25 și Figures 3–5.

- **Figura 2:** fluxul vechi, care includea EWP și plata bursei, a fost înlocuit cu un flux prin cele trei subdomenii, cu bucle pentru mapări, corecturi și documente, plus ramura de retragere.
- **Figura 3:** am scos scheduler-ul de 5 zile și fluxurile de amendare; am păstrat redactarea, trimiterea, verificarea, aprobarea, confirmarea gazdei și anularea.
- **Figura 4:** am adăugat UC02 „Evaluate and publish”, începerea evaluării și respingerea separată.
- **Figura 5:** nominalizarea creează checklistul; UC03 este acum aplicarea evenimentului la checklistul existent. Am ajustat și titlul/legenda exportului ca să nu se suprapună.
- **Figura 8:** am legat modelul DDD de definițiile comune și am schimbat tipurile/stările reprezentate.
- **Figures 9–10:** am înlocuit arhitecturile separate cu vederi bazate pe definiții comune pentru Learning Agreement și Equivalence.
- **Figura 11:** am schimbat ierarhia repository-urilor ca să includă cele trei subdomenii și regulile de persistență ale checklistului.
- **Figures 12–13:** am refăcut integrarea REST ca verificare read-only, cu maparea DTO-ului și rezultate `ELIGIBLE`/`INELIGIBLE`/`UNAVAILABLE`.
- **Figures 14–15:** publicarea evenimentului pornește acum de la confirmarea gazdei; consumatorul actualizează checklistul existent, cu deduplicare, rollback și ACK după commit.
- **Figures 16–18:** am refăcut modelele structurale consolidate folosind definițiile comune ale claselor și pachetelor.
- **Figures 19–21:** am refăcut mașinile de stări pentru acord, echivalență și sarcina de checklist.
- **Figures 22–23:** secvențele descriu acum trimiterea UC01 și publicarea UC02.
- **Figures 24–25:** secvențele descriu confirmarea gazdei/outbox și actualizarea checklistului existent.
- **11 fișiere noi în `docs/diagrams/common/`:** conțin definiții reutilizate pentru clase, enum-uri, arhitecturi și stil, folosite de diagramele structurale.

### Fișiere generate

DOCX-ul a fost regenerat cu textele și imaginile actuale; PDF-ul a fost creat separat. În total, comparația cu originalul arată 77 de fișiere urmărite modificate, plus cele 11 surse PlantUML comune și PDF-ul nou.

---

A domain-driven prototype for modeling international student study mobility under the Erasmus+ framework.

Developed for the **Object-Oriented Analysis and Design (OOAD)** course, Master in Software Development and Business Information Systems (SDBIS / SIA), FEAA, Universitatea „Alexandru Ioan Cuza” din Iași.

---

## 1. Project Overview

The Erasmus Mobility Platform models the academic and administrative steps for preparing a nominated student's study mobility. It separates responsibilities into three bounded contexts.

The software models three specialized Bounded Contexts:
1. **Learning Agreement Management (Core Domain):** Drafting, faculty review, and recording host confirmation evidence for study plans.
2. **Equivalence Management (Supporting Subdomain):** A verified academic catalog matching home faculty courses with foreign university curricula and validating European Credit Transfer and Accumulation System (ECTS) parity.
3. **Mobility Preparation (Supporting Subdomain):** Nomination onboarding, checklist evidence, and readiness tracking. Nomination initializes the checklist; agreement events update its existing academic task.

---

## 2. Team Members and Individual Task Allocation

The project is developed by a team of two graduate students:
* **Prigoreanu Alin-Gabriel** (Student 1)
* **Bîrgovan A. Mihai-Daniel** (Student 2)

Individual responsibilities map directly to course deliverables:

### Student 1: Prigoreanu Alin-Gabriel - Learning Agreement Management (Core Domain) & 50% Mobility Preparation
* **Domain Responsibility:** Core academic workflow and study agreements; 50% joint contribution to Mobility Preparation.
* **Use Case Diagram:** `docs/diagrams/usecase-learning-agreement.puml`
* **Detailed Use Case (SVDPI):** `UC01 - Submit Learning Agreement` (including ECTS balance verification).
* **BDD Specification (Gherkin):** `features/learning-agreement.feature`
* **Dynamic Interaction:** Figure 22 traces UC01 submission; Figure 24 traces host confirmation and outbox publication.
* **State Machine:** Figure 19 models `LearningAgreement` through `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `APPROVED_BY_FACULTY`, `CONFIRMED_BY_HOST`, and `CANCELLED`.

### Student 2: Bîrgovan A. Mihai-Daniel - Equivalence Management (Supporting Subdomain) & 50% Mobility Preparation
* **Domain Responsibility:** Institutional course catalog, syllabus evaluation, and equivalence publication; 50% joint contribution to Mobility Preparation.
* **Use Case Diagram:** `docs/diagrams/usecase-equivalence-management.puml`
* **Detailed Use Case (SVDPI):** `UC02 - Evaluate and publish a course equivalence`.
* **BDD Specification (Gherkin):** `features/equivalence-management.feature`
* **Dynamic Interaction:** Figure 23 traces UC02 evaluation and publication; Figures 12–13 show the read-only REST catalog integration.
* **State Machine:** Figure 20 models `PROPOSED`, `UNDER_EVALUATION`, `ACTIVE`, `REJECTED`, and `RETIRED`.

### Shared Subdomain (50% / 50% Joint Allocation: Prigoreanu Alin-Gabriel & Bîrgovan A. Mihai-Daniel) - Mobility Preparation (Supporting Subdomain)
* **Domain Responsibility:** Checklist tasks and evidence, event consumption, and readiness tracking (co-authored 50% by each student).
* **Use Case Diagram:** `docs/diagrams/usecase-mobility-preparation.puml`
* **Detailed Use Case (SVDPI):** `UC03 - Apply Agreement Event to Mobility Checklist` (host confirmation and cancellation events).
* **BDD Specification (Gherkin):** `features/mobility-preparation.feature`
* **Dynamic Interaction:** Figure 25 applies host-confirmation or cancellation events to the existing checklist; Figure 24 publishes those events through the outbox.
* **State Machine:** Entity `ChecklistTask` via `TaskStatus` enum (`INITIALIZED`, `PENDING_STUDENT_ACTION`, `SUBMITTED_FOR_VERIFICATION`, `COMPLETED`, `OVERDUE`, `ABANDONED`).

---

## 3. Team Deliverables

* **Domain Specification:** Comprehensive narrative detailing subdomains, transactions, and business invariants (`docs/01-subdomains-and-transactions.md`).
* **Non-Functional Requirements:** SLA targets, measurement methods, and audit boundaries (`docs/02-nfr-matrix.md`).
* **Strategic Context Map:** Upstream/Downstream contracts, Shared Kernel, and Open Host Services (`docs/03-context-map-glossary.md`).
* **Cross-Context Activity Diagram:** Figure 2 shows nomination, parallel academic/preparation work, host confirmation, readiness, and withdrawal handling.
* **Structural Models:** Figures 8–18 cover the tactical domain model, layered structures, repositories, integrations, and consolidated context models.
* **Behavioral Models:** Figures 19–21 are state machines; Figures 22–25 are sequence diagrams.
* **Use Case and BDD Specifications:** Figures 3–5, the three narrative use cases, and the matching Gherkin feature files.
* **Generated documentation:** `docs/Erasmus_Mobility_Platform_Documentatie_P1.docx` and `.pdf`.

---

## 4. Repository Structure

```text
erasmus-mobility-platform/
│
├── README.md                           # Current scope, requested changes, and deliverable mapping
│
├── docs/                               # Analysis, architecture memos, and specifications
│   ├── 01-subdomains-and-transactions.md # Subdomain descriptions and T1–T5 transaction flow
│   ├── 02-nfr-matrix.md                # Measurable quality attributes and SLA targets
│   ├── 03-context-map-glossary.md      # Ubiquitous language and integration contracts
│   ├── diagrams/                       # PlantUML sources and shared definitions
│   └── use-cases/                      # Narrative SVDPI use case specifications
│       ├── UC01-submit-learning-agreement.md
│       ├── UC02-register-course-equivalence.md
│       └── UC03-confirm-nomination.md  # Content title: Apply Agreement Event to Mobility Checklist
│
├── features/                           # Gherkin BDD living documentation (.feature files)
│   ├── learning-agreement.feature
│   ├── equivalence-management.feature
│   └── mobility-preparation.feature
│
├── models/                             # Rendered diagram exports
│   └── diagrams-png/                   # PNG and SVG diagrams embedded in the documentation
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


## 5. Development and Tooling

* **PlantUML:** Diagram sources are in `docs/diagrams/`; rendered PNG/SVG exports are in `models/diagrams-png/`.
* **Java and Maven:** The `src/` directory contains the reference domain skeleton and its Maven build.
* **IntelliJ IDEA:** Recommended for inspecting the project and Java sources.

```bash
# Verify build and run architecture constraint checks
cd src
mvn clean test
