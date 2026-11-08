Feature: Academic Equivalence Registration and Catalog Verification
  As a departmental academic evaluator
  I want to review course syllabus parity and register approved equivalences
  So that students can automatically validate course mappings during mobility drafting

  Background:
    Given an authenticated departmental evaluator "Mihai Birgovan" with evaluatorId "ev-2002"
    And access to the "Computer Science" departmental catalog console

  Scenario: Successful registration and publication of academic equivalence
    Given a proposed equivalence between home course "CS301" (Object-Oriented Design, 6 ECTS) and host course "INF405" (Software Architecture, 6 ECTS)
    And the evaluator inputs an assessed syllabus thematic overlap of 85 percent
    And the evaluator specifies a validity window from "2026-10-01" to "2029-09-30"
    When the evaluator confirms the equivalence registration
    Then the platform verifies that curricular parity is at least 80 percent
    And the platform verifies that recognized credits match the 6 ECTS host value
    And the platform transitions the equivalence status to "ACTIVE"
    And the equivalence is indexed and published to the REST catalog endpoint
    And remote clients querying "CS301" and "INF405" receive a valid equivalence response

  Scenario: Rejection of equivalence due to insufficient curricular overlap
    Given a proposed equivalence between home course "CS204" (Algorithms and Data Structures, 6 ECTS) and host course "INF102" (Introduction to Programming, 6 ECTS)
    And the evaluator inputs an assessed syllabus thematic overlap of 55 percent
    When the evaluator attempts to confirm the equivalence registration
    Then the platform blocks approval with error "CURRICULAR_PARITY_DEFICIT"
    And the error message states "Assessed syllabus overlap of 55% is below the mandatory 80% threshold."
    And the equivalence status remains "UNDER_EVALUATION"
    And the record is not published to the public REST catalog endpoint

  Scenario: Prevention of duplicate active equivalence registration
    Given an existing active equivalence in the catalog for "CS301" and "INF405" expiring on "2029-09-30"
    When an evaluator attempts to register a new active equivalence for the identical pair "CS301" and "INF405"
    Then the platform rejects the request with error "DUPLICATE_ACTIVE_RULE"
    And the error message identifies the existing active record ID
    And no redundant catalog entry is created

