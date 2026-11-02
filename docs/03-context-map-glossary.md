# Strategic Context Map & Glosar Ubiquitous Language

**Erasmus Mobility Platform (EMP)**  
**Conformitate:** Domain-Driven Design (Eric Evans, Vaughn Vernon) & Model Proiect 2026 (FEAA Iași)

---

## 1. Harta Strategică de Contexte (Strategic Context Map)

Arhitectura strategică descompune platforma în trei Bounded Context-uri operaționale și două Bounded Context-uri generice:

```mermaid
flowchart TD
    subgraph CoreContext ["Learning Agreement Management (Core Domain)"]
        LA_AR["LearningAgreement (Aggregate Root)"]
        LineA["CourseLineTableA (Entity)"]
        LineB["CourseLineTableB (Entity)"]
    end

    subgraph EquivalenceContext ["Equivalence Management (Supporting Subdomain)"]
        EQ_AR["AcademicEquivalence (Aggregate Root)"]
        Syllabus["CourseSyllabus (Value Object)"]
    end

    subgraph PreparationContext ["Mobility Preparation (Supporting Subdomain)"]
        Task_AR["ChecklistTask (Aggregate Root)"]
        Template["ChecklistTemplate (Entity)"]
    end

    subgraph SharedKernel ["Shared Kernel"]
        SK1["StudentId (Value Object)"]
        SK2["MobilityId (Value Object)"]
        SK3["AcademicPeriod (Value Object)"]
        SK4["ECTSCredits (Value Object)"]
    end

    subgraph GenericContexts ["Generic Subdomains"]
        Notif["Notification Service (Messaging)"]
        Sec["Security & GDPR Audit (RBAC/Auth)"]
    end

    %% Relatii de integrare
    CoreContext -->|Uses| SharedKernel
    EquivalenceContext -->|Uses| SharedKernel
    PreparationContext -->|Uses| SharedKernel

    CoreContext -.->|Sync REST: Search/Validate| EquivalenceContext
    CoreContext == Transactional Outbox ==>|Async Event: LA Approved/Cancelled| PreparationContext
    PreparationContext -.->|Trigger Notif| Notif
    CoreContext -.->|Trigger Notif| Notif
    CoreContext -.->|Audit Log| Sec
    EquivalenceContext -.->|Audit Log| Sec
```

### Tipuri de Contracte de Integrare Formalizate:
1. **Shared Kernel:** Contextele partajează tipurile de date imuabile fundamentale: `StudentId`, `MobilityId`, `AcademicPeriod` și `ECTSCredits`. Orice modificare a acestor tipuri necesită consens între toate echipele.
2. **Customer / Supplier (Sincron REST cu Adapter):** Subdomeniul *Learning Agreement* este consumator (Customer) al serviciilor expuse de *Equivalence Management* (Supplier). Interogarea compatibilității dintre cursurile Table A și Table B se face printr-un port în Domain Layer și un adaptor REST în Infrastructure Layer.
3. **Asynchronous Domain Events (Transactional Outbox):** Comunicarea între *Learning Agreement* și *Mobility Preparation* este complet asincronă și decuplată temporal. Evenimentele de domeniu (`LearningAgreementApprovedEvent`, `LearningAgreementCancelledEvent`) sunt salvate atomic în tabela Outbox a contextului emițător și expediate garantat către broker, fiind consumate idempotent în *Mobility Preparation*.

---

## 2. Glosarul Ubiquitous Language

| Termen / Concept | Context Delimitat (Bounded Context) | Tip DDD / Rol | Definiție de Afaceri și Semnificație Arhitecturală |
| :--- | :--- | :--- | :--- |
| **LearningAgreement** | Learning Agreement Management | **Aggregate Root** | Contractul educațional tripartit oficial încheiat între student, facultatea de origine și universitatea parteneră. Garantează recunoașterea academică automată a creditelor la finalizarea cu succes a mobilității. |
| **CourseLineTableA** | Learning Agreement Management | **Entity** | Reprezintă o disciplină din planul de învățământ al universității primitoare (gazdă) pe care studentul o va frecventa, având un cod extern, denumire, semestru și credite ECTS. |
| **CourseLineTableB** | Learning Agreement Management | **Entity** | Reprezintă o disciplină din planul de învățământ al facultății de trimitere (UAIC) care va fi echivalată la întoarcere în baza promovării cursurilor din Table A. |
| **StareLearningAgreement** | Learning Agreement Management | **Enum / Value Object** | Valorile permise pentru ciclul de viață al contractului: `Ciorna`, `Trimis`, `InRevizuire`, `AprobatFacultate`, `ConfirmatPartener`, `Amendat`, `Anulat`. |
| **AcademicEquivalence** | Equivalence Management | **Aggregate Root** | Regula formală instituțională care leagă o disciplină sau un grup de discipline externe de o disciplină locală, pe baza similitudinii de conținut și a creditelor transferabile. |
| **StareEchivalare** | Equivalence Management | **Enum / Value Object** | Stările posibile ale unei reguli de echivalare: `Propusa`, `InEvaluare`, `Aprobata`, `Activa`, `Retrasa`. |
| **ChecklistTask** | Mobility Preparation | **Aggregate Root** | Sarcină administrativă individuală alocată unui student nominalizat (ex: testare OLS, adeverință EHIC, contract financiar) cu termen limită de rezolvare. |
| **StareSarcina** | Mobility Preparation | **Enum / Value Object** | Stările posibile ale unei sarcini din checklist: `Initializata`, `InAsteptareDocument`, `TrimisaSpreValidare`, `Finalizata`, `Depasita`. |
| **StudentId** | Shared Kernel | **Value Object** | Identificator unic de tip UUID/număr matricol care identifică studentul în mod unic la nivelul întregului sistem universitar. |
| **MobilityId** | Shared Kernel | **Value Object** | Identificator unic al dosarului de mobilitate deschis în urma procesului de selecție și alocare a unui loc la o universitate parteneră. |
| **AcademicPeriod** | Shared Kernel | **Value Object** | Interval temporal compus din `dataInceput` și `dataSfarsit`, garantând invariantul `dataSfarsit >= dataInceput`. |
| **ECTSCredits** | Shared Kernel | **Value Object** | Valoare numerică ce cuantifică volumul de muncă asociat unei discipline, garantând invariantul ca valoarea să fie pozitivă și conformă normelor sistemului european de transfer al creditelor. |

