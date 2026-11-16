# UC03 — Apply Agreement Event to Mobility Checklist

* **Authors:** Prigoreanu Alin-Gabriel (Student 1, 50%) & Bîrgovan A. Mihai-Daniel (Student 2, 50%)
* **Subdomain:** Mobility Preparation (Supporting Subdomain)
* **Primary Aggregate:** `MobilityChecklist` / `ChecklistTask`
* **Traceability:** Figure 5 (use case), Figure 25 (sequence), Figure 21 (task state machine), `mobility-preparation.feature`

## Goal

Apply a confirmed agreement or cancellation event to the preparation checklist that was initialized when DRI registered the existing nomination. The event consumer is idempotent and does not create a checklist.

## Actors and Preconditions

* **Primary actor:** Learning Agreement publishing module, through the message broker.
* **Supporting system:** Mobility Preparation message receiver.
* A checklist exists for the event's `MobilityId`; its academic confirmation task is awaiting confirmation.
* The event contains a unique `eventId`, matching agreement and mobility identifiers, and an ordered `sourceVersion`.

## Main Success Scenario — Host Confirmation

| Step | Initiator | Interaction |
| :--- | :--- | :--- |
| 1 | Broker | Delivers a `HOST_CONFIRMED` agreement event. |
| 2 | Receiver | Passes the event to the application service. |
| 3 | Service | In one local transaction, reserves `eventId` in the processed-event ledger. |
| 4 | Service | Loads the existing checklist by `MobilityId` and verifies the agreement identity. |
| 5 | Checklist | Applies the ordered event; the awaiting academic task transitions to `COMPLETED`. |
| 6 | Service | Saves the checklist and commits the task update with the event record. |
| 7 | Receiver | Acknowledges the broker message after commit. |

**Success postcondition:** The existing checklist records host confirmation exactly once. This operation does not confirm overall departure readiness.

## Alternatives and Exceptions

* **Duplicate `eventId`:** Make no changes and acknowledge the already processed message.
* **Missing checklist or mismatched agreement:** Roll back the event record and request redelivery; do not create a dossier.
* **Stale confirmation or confirmation after cancellation:** Keep the cancellation effective, commit the handled event without reactivating the checklist, then acknowledge it.
* **New cancellation event:** Mark the checklist cancelled and abandon active tasks; preserve completed evidence as history.
* **Save or concurrency failure:** Roll back the checklist change and event record; do not acknowledge, allowing retry.

Nomination registration and checklist initialization are separate use cases shown in Figure 5. Scholarship payment, EWP exchange, and production identity are outside this project scope.
