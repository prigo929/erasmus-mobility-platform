Feature: Learning Agreement Management and Invariant Enforcement
  As an outgoing exchange student
  I want to assemble and submit my Learning Agreement
  So that my academic recognition is guaranteed by both home and host faculties

  Background:
    Given an authenticated student "Alin Prigoreanu" with studentId "s-1001"
    And an active nomination to "Technical University of Munich" for the "Winter 2026" semester
    And an empty learning agreement draft with status "DRAFT"

  Scenario: Successful submission of a credit-balanced learning agreement
    Given the student adds the following host courses to Table A:
      | Course Code | Course Title                 | ECTS Credits |
      | IN2001      | Advanced Software Engineering | 8.0          |
      | IN2002      | Distributed Systems           | 7.0          |
      | IN2003      | Cloud Computing Architecture | 8.0          |
      | IN2004      | Database Internals           | 7.0          |
    And the student maps the following recognized home courses in Table B:
      | Course Code | Course Title             | ECTS Credits |
      | CS-M101     | Software Design Patterns | 8.0          |
      | CS-M102     | Distributed Systems Lab  | 7.0          |
      | CS-M103     | Cloud Infrastructure     | 8.0          |
      | CS-M104     | Advanced Databases       | 7.0          |
    When the student submits the learning agreement
    Then the platform verifies that Table A total ECTS is 30.0
    And the platform verifies that Table B total ECTS is 30.0
    And the platform transitions the agreement status to "SUBMITTED"
    And all course lines in Table A and Table B become immutable
    And a submission receipt is issued to "Alin Prigoreanu"

  Scenario: Rejection of agreement submission due to credit volume deficit
    Given the student adds the following host courses to Table A:
      | Course Code | Course Title                 | ECTS Credits |
      | IN2001      | Advanced Software Engineering | 8.0          |
      | IN2002      | Distributed Systems           | 7.0          |
      | IN2003      | Cloud Computing Architecture | 8.0          |
    And the student maps the following recognized home courses in Table B:
      | Course Code | Course Title             | ECTS Credits |
      | CS-M101     | Software Design Patterns | 8.0          |
      | CS-M102     | Distributed Systems Lab  | 7.0          |
      | CS-M103     | Cloud Infrastructure     | 8.0          |
    When the student attempts to submit the learning agreement
    Then the platform rejects the submission with error "INSUFFICIENT_CREDITS"
    And the error message states "Total host credits must be at least 30.0 ECTS. Current total is 23.0 ECTS."
    And the agreement status remains "DRAFT"
    And course lines in Table A remain open for editing

  Scenario: Rejection of agreement submission due to credit parity discrepancy
    Given the student adds host courses to Table A totaling 30.0 ECTS
    But the student maps home courses in Table B totaling only 25.0 ECTS
    When the student attempts to submit the learning agreement
    Then the platform rejects the submission with error "CREDIT_PARITY_MISMATCH"
    And the error message states "Table A credits (30.0) do not equal Table B credits (25.0)."
    And the agreement status remains "DRAFT"

