Feature: Mobility Preparation Checklist and Departure Gate Verification
  As an institutional mobility officer
  I want to verify student onboarding document proofs and confirm departure readiness
  So that outgoing students comply with legal, medical, and grant regulations

  Background:
    Given an authenticated mobility officer "Ana-Maria Schipor" with officerId "off-3003"
    And an outgoing exchange student "s-1001" with an approved learning agreement "la-9001"

  Scenario: Successful checklist completion and departure clearance
    Given an inbound message on "mobility.preparation.agreement.approved" with eventId "evt-8801"
    When the message receiver processes the event
    Then a new MobilityChecklist is instantiated for student "s-1001"
    And the checklist contains the default mandatory tasks:
      | Task Code | Title                     | Mandatory | Initial Status         |
      | TASK-01   | Erasmus+ Grant Agreement  | true      | PENDING_STUDENT_ACTION |
      | TASK-02   | Health Insurance Proof    | true      | PENDING_STUDENT_ACTION |
      | TASK-03   | Host Acceptance Letter    | true      | PENDING_STUDENT_ACTION |
    When the student uploads valid PDF proofs for all mandatory tasks
    And the mobility officer reviews and approves all attached proofs
    Then all mandatory tasks transition to status "COMPLETED"
    And the departure gate evaluates "areMandatoryTasksComplete()" as true
    And the checklist status transitions to "CONFIRMED_READY_FOR_DEPARTURE"
    And the first grant installment is unlocked for disbursement

  Scenario: Departure gate blocks confirmation when a mandatory task is overdue
    Given an active MobilityChecklist for student "s-1001" with a deadline of "2026-08-15"
    And the student uploaded the grant agreement and acceptance letter
    But the student failed to submit the health insurance proof before "2026-08-15"
    When the daily compliance scanner runs on "2026-08-16"
    Then the health insurance task status transitions to "OVERDUE"
    When the mobility officer attempts to confirm departure readiness
    Then the platform rejects confirmation with error "MANDATORY_TASKS_INCOMPLETE"
    And the error message lists "Health Insurance Proof (OVERDUE)" as blocking departure
    And the checklist status remains "IN_PROGRESS"
    And grant disbursement remains locked

  Scenario: Idempotent message consumption prevents duplicate checklist creation
    Given that eventId "evt-8801" already exists in the "processed_events" table
    When a duplicate AMQP message with eventId "evt-8801" is delivered to the receiver
    Then the platform detects the event identifier in the idempotency ledger
    And the application service skips checklist instantiation
    And the receiver acknowledges the message with channel basicAck
    And exactly one checklist remains associated with student "s-1001"

