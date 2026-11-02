# Measurable Non-Functional Requirements (NFR) Matrix with SLA Targets

**Erasmus Mobility Platform (EMP)**  
**Methodological Alignment:** Course Chapter 2 - Functional Modeling (FEAA Master SDBIS / SIA)  
**Specification Standard:** Every non-functional requirement specifies an architectural category, a quantifiable metric, an explicit Service Level Agreement (SLA) threshold, a verification method, and the corresponding architectural decision.

---

## 1. Methodological Foundations

According to Dennis et al. and course lectures:
> *"A functional requirement decides which classes and operations must exist. A non-functional requirement decides which architecture you need (layering, caching, database partitioning, asynchronous event processing, security boundaries)."*  
> *"Statements like 'the system must be fast and user-friendly' are wishes, not requirements. Make them measurable or delete them."*

The following matrix governs the architectural quality attributes of the Erasmus Mobility Platform.

---

## 2. Extended Quality Attribute Matrix

| ID | Architectural Category | Measurable Quality Attribute | Quantifiable Metric | Service Level Agreement (SLA Target) | Verification & Testing Condition | Architectural Decision & Implementation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NFR-01** | **Performance & Latency** | Equivalence Catalog Search Response Time | HTTP Endpoint Latency (p95, p99) | **p95 < 250 ms**, **p99 < 500 ms** | Gatling / JMeter load test executing 100 concurrent multi-attribute filter queries (partner university, country, degree program) against a database holding at least 50,000 course syllabus records. | Composite B-Tree index on `(partner_id, course_code)`, PostgreSQL query plan optimization, and Redis / Hibernate L2 Cache for active semester partner catalogs. |
| **NFR-02** | **Performance & Integrity** | ECTS Parity Validation Execution Latency | In-Memory Method Execution Duration | **Latency < 100 ms** | Automated JMH / JUnit benchmark executing `LearningAgreement.validateEctsBalance()` on contracts holding up to 30 curricular lines (Table A / Table B). | Pure in-memory Domain Model execution within the Aggregate Root boundary, free of blocking I/O or downstream remote service calls. |
| **NFR-03** | **Security & Compliance (GDPR)** | Tamper-Evident Immutable Audit Trail | Capture Ratio & Persistence Write Latency | **100% of mutating actions captured**, synchronous persistence in **< 20 ms** | Automated security test asserting that all grade modifications, approval signatures, and PII accesses (National ID, bank IBAN) generate an append-only ledger entry signed with HMAC SHA-256. | Spring Security AOP Aspect (`@Audited`), dedicated append-only ledger table with restricted database update/delete privileges. |
| **NFR-04** | **Scalability & Batch Processing** | Automated Deadline Sweep & Reminder Dispatching | Batch Job Execution Throughput | **10,000 active dossiers processed in < 60 seconds** | Nightly batch benchmark scanning 10,000 student mobility dossiers, computing milestone intervals (T-7, T-3, Overdue), and queuing alert payloads. | Asynchronous Spring Batch / Scheduled Task accelerated by Java 23 Virtual Threads, partitioned database pagination, and RabbitMQ message broker. |
| **NFR-05** | **Transactional Consistency** | State Convergence on Mobility Abort (Interruptible Region) | End-to-End State Convergence Window | **Atomic ACID consistency** (single transaction) or eventual consistency in **< 1,500 ms** | Distributed integration test asserting that invoking `CancelMobility` cascades state transitions across `LearningAgreement` (`CANCELLED`) and active `ChecklistTask` records (`ABORTED`). | **Transactional Outbox Pattern**: state mutation and `MobilityCancelledEvent` committed within the same ACID boundary, followed by idempotent downstream message consumption. |
| **NFR-06** | **Availability & Resilience** | Platform Operational Availability during Peak Submission Windows | Monthly Operational Uptime | **Availability ≥ 99.5%** during peak academic windows (September–October & January–February); **MTTR < 15 minutes** | Continuous synthetic probing via Prometheus and Grafana on the `/actuator/health` endpoint under simulated peak concurrency; automated container self-healing. | Containerized multi-instance deployment on Kubernetes, Horizontal Pod Autoscaling (HPA) driven by CPU/memory thresholds, and PostgreSQL active-passive read replica failover. |
| **NFR-07** | **Security & Authorization** | Role-Based Access Control Segregation (RBAC) | Unauthorized Access Rejection Rate | **100% unauthorized requests rejected** (HTTP 403 Forbidden) | Automated OWASP Top 10 Broken Access Control test suite attempting cross-student contract modification and privilege escalation. | Federated eduGAIN / OAuth2 JWT authentication, Spring Security method-level `@PreAuthorize`, and entity tenancy verification `SecurityContext.getCurrentStudentId() == LA.getStudentId()`. |
