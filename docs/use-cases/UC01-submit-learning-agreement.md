# UC01 — Submit Learning Agreement

* **Author:** Prigoreanu Alin-Gabriel (Student 1)
* **Subdomain:** Learning Agreement Management
* **Primary aggregate:** `LearningAgreement`
* **Traceability:** Figure 3 (use case), Figure 22 (sequence), Figure 19 (full agreement lifecycle), `learning-agreement.feature`

## Goal and actors

The student submits an editable semester study plan for home-faculty review. The system checks each explicit 1:1 course mapping against the read-only Equivalence catalog before allowing submission.

* **Primary actor:** Student who owns the draft.
* **Supporting system:** Equivalence Management through `IEquivalenceCatalogAdapter` / `EquivalenceRestAdapter`.
* **Later lifecycle actors:** Home Academic Coordinator reviews the submitted agreement; DRI records host evidence and cancellation. These later steps are shown in Figure 19 and are outside UC01's success postcondition.

## Preconditions

1. An active nomination exists for the student and semester.
2. The student owns a persisted `DRAFT` Learning Agreement and has its current version.
3. Course mappings and their catalog references can be loaded.

## Main success scenario

| Step | Actor | Action / response |
|---|---|---|
| 1 | Student | Requests submission of the current draft. |
| 2 | System | Loads the agreement and checks ownership, `DRAFT` status, and expected version. |
| 3 | System | For each `RecognitionMapping`, checks the 1:1 rule and queries the catalog for the exact courses, versions, and mobility period. |
| 4 | Catalog | Returns `ELIGIBLE` for every mapping; the adapter translates each DTO into a domain verification result. |
| 5 | System | The aggregate verifies equal recognized credits, no duplicate counting, and at least 30 ECTS for the semester (project policy). |
| 6 | System | In one local transaction, changes `DRAFT` to `SUBMITTED` and saves the agreement and decision using the expected version. |
| 7 | System | Commits and returns a submission receipt. The student can no longer edit the submitted version. |

**Success postcondition:** The persisted status is `SUBMITTED`; the agreement and audit decision are committed together. Figure 22 shows this transaction and its failure branches. Figure 19 continues the lifecycle after submission.

## Alternatives and failures

* **Catalog returns `INELIGIBLE`:** Stop before submission, explain which mapping failed, and keep the persisted agreement `DRAFT` for correction.
* **Catalog returns `UNAVAILABLE`:** Stop before submission and offer retry; unavailability is not academic rejection. Keep `DRAFT`.
* **Credit total is below 30 ECTS, credits differ, mappings are invalid, or the state is not `DRAFT`:** Reject the command without changing persisted state; explain the failed rule.
* **The agreement version changed or persistence fails:** Roll back the local transaction, return a conflict, and ask the student to reload. Do not report successful submission.

## Rules

* Every submitted mapping is explicit and 1:1; its host and home credits must be equal.
* Each mapping must be eligible for the whole mobility period; aggregate credit totals do not replace mapping checks.
* The semester minimum of 30 ECTS is a project policy.
* A failed request leaves the persisted draft editable; a successful request commits `SUBMITTED` and its decision atomically.
