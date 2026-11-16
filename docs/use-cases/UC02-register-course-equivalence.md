# UC02 — Evaluate and publish a course equivalence

* **Author:** Bîrgovan A. Mihai-Daniel (Student 2)
* **Subdomain:** Equivalence Management
* **Primary aggregate:** `AcademicEquivalence`
* **Traceability:** Figure 4 (use case), Figure 23 (sequence), Figure 20 (full equivalence lifecycle), `equivalence-management.feature`

## Goal and actors

An authorized Home Academic Coordinator evaluates an existing course-equivalence proposal and publishes it to the catalog when all project rules pass.

* **Primary actor:** Home Academic Coordinator / evaluator.
* **Supporting caller:** Learning Agreement consults active rules through the read-only catalog API; it does not publish proposals.

## Preconditions

1. The proposal exists and is in `UNDER_EVALUATION`.
2. The evaluator is authorized and has the proposal's current version.
3. The evaluator has recorded a score, rationale, and validity window for the requested mobility period.
4. `beginEvaluation(actorId)` was committed earlier; starting evaluation is a separate action from UC02's publication transaction.

## Main success scenario

| Step | Actor | Action / response |
|---|---|---|
| 1 | Coordinator | Submits `evaluateAndPublish(cmd)` with the score, rationale, period, actor, and expected version. |
| 2 | System | Loads the proposal and verifies authorization, `UNDER_EVALUATION`, and expected version. |
| 3 | System | Checks the proposed active-rule key and validity window for overlap. |
| 4 | Aggregate | Verifies the didactic score threshold (at least 80/100), equal credits, a valid period covering the requested mobility, and a non-empty rationale. |
| 5 | System | In one local transaction, saves `ACTIVE` and its decision with an optimistic version check and persistence-level protection against concurrent overlapping publication. |
| 6 | System | Commits and confirms that the rule is available to catalog searches and Learning Agreement checks. |

**Success postcondition:** The proposal is persisted as `ACTIVE` with its decision and validity window. Figure 23 shows the publication transaction and failure branches; Figure 20 shows the preceding `PROPOSED` → `UNDER_EVALUATION` lifecycle and later retirement.

## Alternatives and failures

* **Proposal missing, evaluator unauthorized, wrong state, or stale version:** Reject before publication; leave the catalog unchanged.
* **Score, rationale, credits, or validity fails validation:** Reject the command and retain `UNDER_EVALUATION` so the proposal can be corrected. This is not an explicit rejection decision.
* **An overlapping active rule exists:** Report the conflict; do not publish.
* **A concurrent publication or persistence failure occurs:** Roll back, retain the unpublished proposal, and require reload/review. The initial overlap query alone is not the uniqueness guarantee.
* **Evaluator explicitly rejects:** This is the separate `reject(actorId, reason)` use case shown in Figure 4 and Figure 20; it requires a reason and transitions to `REJECTED`.

## Rules

* The 80/100 threshold is a project policy, not a universal Erasmus rule.
* Recognized and host credits must be equal for this project.
* The validity window must cover the whole mobility period; overlapping active rules for the same course pair are prohibited.
* Approval and publication are one operation: there is no intermediate `APPROVED` state.
