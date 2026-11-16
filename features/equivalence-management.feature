Feature: UC02 evaluate and publish a course equivalence
  An authorized coordinator publishes an existing proposal only after project
  validation and overlap protection succeed.

  Background:
    Given an authorized Home Academic Coordinator
    And a persisted equivalence proposal in "UNDER_EVALUATION"
    And the coordinator has the current proposal version

  Scenario: Publish an eligible proposal
    Given the score is 85 out of 100 with a recorded rationale
    And host and home credits are equal
    And the validity window covers the full mobility period
    And no overlapping active rule exists for the course pair
    When the coordinator evaluates and publishes the proposal
    Then "ACTIVE" and the decision are committed in one local transaction
    And the rule is available through the read-only catalog API

  Scenario: Score is below the project threshold
    Given the score is 79 out of 100 with a recorded rationale
    When the coordinator evaluates and publishes the proposal
    Then publication is rejected by the project threshold of 80 out of 100
    And the proposal remains "UNDER_EVALUATION"
    And the proposal is not available in the catalog

  Scenario: Rationale is missing
    Given the score is 85 out of 100 but no rationale is recorded
    When the coordinator evaluates and publishes the proposal
    Then publication is rejected with a missing-rationale error
    And the proposal remains "UNDER_EVALUATION"

  Scenario: An active rule overlaps the requested period
    Given an active rule already covers the same course pair and period
    When the coordinator evaluates and publishes the proposal
    Then publication is rejected with an overlap conflict
    And no second active rule is created

  Scenario: A concurrent publication wins the version check
    Given another publication changes the course-pair rule before this save
    When the coordinator evaluates and publishes the proposal
    Then the local transaction rolls back with a conflict
    And the proposal is not reported as "ACTIVE"
    And the coordinator is asked to reload the proposal

  Scenario: The coordinator explicitly rejects the proposal
    Given the coordinator records a rejection reason
    When the coordinator rejects the proposal
    Then the proposal transitions to "REJECTED"
    And the rejection reason is retained in its decision history
