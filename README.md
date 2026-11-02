# erasmus-mobility-platform

# Sistem Integrat de Gestiune a Mobilităților Erasmus+ (Erasmus Mobility Platform)

Proiect semestrial la disciplina **Analiza și Proiectarea Orientate pe Obiecte**
Master SDBIS / SIA, Anul I, Semestrul I, Universitatea „Alexandru Ioan Cuza” din Iași

## Echipa de proiect și atribuirea sarcinilor

### Student 1: [Nume Student 1]
* **Subdomeniu:** Gestiunea Candidaturilor și a Mobilităților (Core Domain)
* **Diagramă Use Case:** Procesul de înscriere și selecție dosare
* **Use Case Documentat (SVDPI & Gherkin):** `UC01 - Depunere Dosar Candidatură`
* **Diagramă de Secvență:** Interacțiunea sincronă de validare a mediei academice
* **Diagramă de Stări (State Machine):** Ciclul de viață al entității `CandidaturaMobilitate` (`Enum StareCandidatura`)

### Student 2: [Nume Student 2]
* **Subdomeniu:** Acorduri Academice și Echivalare ECTS (Supporting Subdomain)
* **Diagramă Use Case:** Gestiunea contractelor de studii și echivalare credite
* **Use Case Documentat (SVDPI & Gherkin):** `UC02 - Aprobare Learning Agreement`
* **Diagramă de Secvență:** Aprobarea tripartită a pachetului de discipline
* **Diagramă de Stări (State Machine):** Ciclul de viață al entității `LearningAgreement` (`Enum StareLearningAgreement`)

### Student 3: [Nume Student 3]
* **Subdomeniu:** Gestiune Financiară și Deconturi (Supporting Subdomain)
* **Diagramă Use Case:** Alocare granturi, plăți avans și regularizări
* **Use Case Documentat (SVDPI & Gherkin):** `UC03 - Calculare și Aprobare Grant Financiar`
* **Diagramă de Secvență:** Integrarea asincronă Outbox la finalizarea stagiului
* **Diagramă de Stări (State Machine):** Ciclul de viață al entității `DosarBursa` (`Enum StareDosarBursa`)
* **Partea a II-a (Design Patterns):** Arhitectura Strategy + Factory + Singleton + Facade pentru calculul granturilor pe grupuri de țări

## Componente comune de echipă
* Descrierea spațiului problemei și Context Map
* Diagrama de activitate unică peste toate Bounded Context-urile (cu swimlanes și zonă de întrerupere)
* Pachetul structural complet (Diagramele de clasă Fig. 8 - 15)
