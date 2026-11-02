# Chapter 4. Repository Hierarchy Architecture (Figure 11)

**Erasmus Mobility Platform (EMP)**  
**Methodological Alignment:** Tactical Domain-Driven Design (Eric Evans) & Course Repository Specifications (FEAA Master SDBIS / SIA)  
**Visual Artifact:** [`models/diagrams-png/Figura11-Repository-Hierarchy.png`](file:///Users/alinprigoreanu/Documents/Object-oriented analysis and design/erasmus-mobility-platform/models/diagrams-png/Figura11-Repository-Hierarchy.png)  
**Scalable Vector Graphics (SVG):** [`models/diagrams-png/Figura11-Repository-Hierarchy.svg`](file:///Users/alinprigoreanu/Documents/Object-oriented analysis and design/erasmus-mobility-platform/models/diagrams-png/Figura11-Repository-Hierarchy.svg)  
**PlantUML Source:** [`docs/diagrams/fig11-repository-hierarchy.puml`](file:///Users/alinprigoreanu/Documents/Object-oriented analysis and design/erasmus-mobility-platform/docs/diagrams/fig11-repository-hierarchy.puml)

---

## 1. Tactical Purpose of the Repository Pattern

In Domain-Driven Design, a repository provides the illusion of an in-memory collection of all aggregate roots of a given type. It mediates between the domain model and data mapping layers.

The architecture enforces a strict physical separation:
1. **The Domain Layer owns the interface:**  
   The interface (`LearningAgreementRepo`, `ChecklistTaskRepo`) defines the persistence contract. It resides in the domain package. It knows only about domain entities, value objects, and domain exceptions.
2. **The Infrastructure Layer owns the implementation:**  
   The concrete class (`LearningAgreementRepoJPA`, `ChecklistTaskRepoJPA`) resides in the infrastructure package. It imports Hibernate, JPA annotations, and relational drivers.

---

## 2. The Abstract Base: `AbstractRepositoryJPA`

All concrete repository implementations extend `AbstractRepositoryJPA`. 

```java
package ro.uaic.feaa.erasmus.infrastructure.persistence;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import java.io.Serializable;
import java.util.Optional;

public abstract class AbstractRepositoryJPA<T, ID extends Serializable> {

    @PersistenceContext
    protected EntityManager em;

    protected final Class<T> entityClass;

    protected AbstractRepositoryJPA(Class<T> entityClass) {
        this.entityClass = entityClass;
    }

    public Optional<T> findById(ID id) {
        return Optional.ofNullable(em.find(entityClass, id));
    }

    public void add(T entity) {
        em.persist(entity);
    }

    public void save(T entity) {
        em.merge(entity);
    }

    public void delete(T entity) {
        em.remove(em.contains(entity) ? entity : em.merge(entity));
    }
}
```

### The Transactional Boundary Rule
The base class exposes persistence operations. It declares zero transaction boundaries. 
* Transactions belong in the **Application Service Layer** via `@Transactional`.
* If a repository method managed its own transaction, calling `findById`, updating course lines, and writing an outbox event would run in separate database commits. A system crash halfway through would produce orphaned database records.
* Application Services open the transaction at the start of a command, execute all domain operations, and close the transaction in one atomic commit.

---

## 3. Structural Breakdown of Repository Classes

### 3.1 `LearningAgreementRepo` (Core Domain)
* **Domain Interface:** Exposes `add`, `findById`, `findByStudentId`, `save`, and `delete`.
* **Concrete JPA Class:** `LearningAgreementRepoJPA` extends `AbstractRepositoryJPA<LearningAgreement, UUID>`.
* **Responsibility:** Loads and persists the complete `LearningAgreement` aggregate. It loads all `CourseLineTableA` and `CourseLineTableB` lines within the same entity graph.

### 3.2 `CourseLineQueryRepo` (Read-Only Projection)
* **Domain Interface:** Exposes projection queries `findLinesByAgreementId` and `findHostCourseByCode`.
* **Concrete JPA Class:** `CourseLineQueryRepoJPA` uses JPA Criteria queries to return read-only DTO records.
* **Invariant Constraint:** Direct mutations through this repository are forbidden. Adding, editing, or deleting lines must traverse `LearningAgreement` root methods to protect the 30 ECTS invariant.

### 3.3 `AcademicEquivalenceRepo` (Supporting Subdomain)
* **Domain Interface:** Exposes `save`, `findById`, `searchByPartnerAndCode`, and `findActiveByDegreeProgram`.
* **Concrete JPA Class:** `AcademicEquivalenceRepoJPA` queries syllabus mappings.
* **Type Safety:** Returns typed `AcademicEquivalence` aggregates and `CourseSyllabus` value objects.

### 3.4 `ChecklistTaskRepo` (Supporting Subdomain)
* **Domain Interface:** Exposes `save`, `findById`, `findAllByMobilityId`, and `findOverdueTasks`.
* **Concrete JPA Class:** `ChecklistTaskRepoJPA` queries student administrative onboarding tasks.
* **Batch Scheduling:** Supports indexed date queries for the nightly temporal deadline sweep.

