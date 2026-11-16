Feature: UC03 apply an agreement event to the existing mobility checklist
  As the Mobility Preparation message receiver
  I want to apply ordered agreement events exactly once
  So that host confirmation completes the academic task and cancellation stays effective

  Background:
    Given an existing mobility checklist "mob-1001" for agreement "la-9001"
    And its academic confirmation task is "PENDING_STUDENT_ACTION"

  Scenario: Host confirmation completes the existing academic task
    Given a valid "HOST_CONFIRMED" event "evt-101" for source version 4
    When the receiver applies the event
    Then the academic task transitions to "COMPLETED"
    And the checklist and processed event are committed in one local transaction
    And the receiver acknowledges the broker message after commit
    And departure readiness is not automatically confirmed

  Scenario: Duplicate delivery is acknowledged without applying twice
    Given event "evt-101" is already in the processed-event ledger
    When the receiver processes the duplicate delivery
    Then the checklist is unchanged
    And the receiver acknowledges the duplicate message

  Scenario: Missing checklist causes retry without creating a dossier
    Given no checklist exists for mobility "mob-1001"
    And a valid "HOST_CONFIRMED" event "evt-102" is delivered
    When the receiver applies the event
    Then the event-ledger insertion is rolled back
    And no checklist is created
    And the receiver does not acknowledge the message

  Scenario: Cancellation remains effective against a stale confirmation
    Given the checklist was cancelled at source version 5
    And a "HOST_CONFIRMED" event for source version 4 is delivered
    When the receiver applies the event
    Then the checklist remains cancelled
    And the stale event is recorded as handled
    And the receiver acknowledges the message
