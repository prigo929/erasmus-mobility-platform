Feature: UC01 submit a Learning Agreement
  A student submits a versioned semester draft after every explicit course mapping
  passes the read-only equivalence check and the aggregate credit rules.

  Background:
    Given an active nomination exists for the student and semester
    And the student owns a persisted Learning Agreement in "DRAFT"
    And the student has the current agreement version

  Scenario: Submit a valid agreement
    Given the draft contains eligible 1:1 mappings for the full mobility period
    And the mapped host and home credits are equal
    And the agreement totals at least 30 ECTS for the semester
    When the student submits the current draft
    Then the system checks each mapping through the read-only catalog adapter
    And the agreement and decision are committed as "SUBMITTED" using the expected version
    And the student receives a submission receipt

  Scenario: A mapping is ineligible
    Given one mapping receives the catalog result "INELIGIBLE"
    When the student submits the current draft
    Then submission is rejected with the failed mapping identified
    And the persisted agreement remains "DRAFT"

  Scenario: The catalog is unavailable
    Given one mapping receives the catalog result "UNAVAILABLE"
    When the student submits the current draft
    Then submission is rejected as retryable and is not treated as academic rejection
    And the persisted agreement remains "DRAFT"

  Scenario: The semester credit minimum is not met
    Given otherwise eligible mappings total 29 ECTS
    When the student submits the current draft
    Then submission is rejected by the project minimum of 30 ECTS
    And the persisted agreement remains "DRAFT"

  Scenario: Mapped course credits differ
    Given one eligible 1:1 mapping has unequal host and home credits
    When the student submits the current draft
    Then submission is rejected with a credit-parity error
    And the persisted agreement remains "DRAFT"

  Scenario: The draft changed after it was loaded
    Given another update has advanced the agreement version
    When the student submits using the stale expected version
    Then the local submission transaction rolls back with a version conflict
    And no successful receipt is returned
    And the student is asked to reload the agreement
