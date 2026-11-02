# Matricea Cerințelor Non-Funcționale (NFR) cu SLA Măsurabil

**Erasmus Mobility Platform (EMP)**  
**Conformitate:** Cursul C2-C3 Functional Modeling (FEAA Iași)  
**Standard formulare:** Fiecare cerință conține un prag măsurabil, o unitate de măsură și o condiție explicită de testare/validare.

---

## 1. Principii Metodologice

Conform cursului de Analiză și Proiectare Orientată Obiect:
> *„O cerință funcțională decide ce clase și operații trebuie să existe. O cerință non-funcțională decide ce arhitectură trebuie adoptată (stratificare, caching, baze de date, procesare asincronă, securitate).”*  
> *„Formularea 'sistemul trebuie să fie ușor de folosit sau rapid' nu este o cerință, ci o dorință. Transformați-o într-o măsurătoare cuantificabilă sau eliminați-o.”*

Fiecare cerință non-funcțională din această matrice este legată direct de deciziile arhitecturale adoptate în sistemul EMP.

---

## 2. Matricea Extinsă a Cerințelor Non-Funcționale

| ID | Categorie Arhitecturală | Cerință Non-Funcțională | Indicator / Metrică | Nivel de Serviciu Garantat (SLA) | Metodă & Condiție de Verificare | Decizie Arhitecturală Asociată |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NFR-01** | **Performanță** | Timp de răspuns la căutarea în catalogul de echivalări | Latență interogare HTTP (p95, p99) | **p95 < 250 ms**, **p99 < 500 ms** | Test de sarcină Gatling/JMeter: 100 de utilizatori concurenți executând căutări combinate (universitate + domeniu + semestru) pe o bază de date cu cel puțin 50.000 de materii. | Index compus B-Tree pe `(partener_id, cod_disciplina)`, caching L2 Redis pentru cataloagele partenere active. |
| **NFR-02** | **Performanță & Integritate** | Latență la validarea creditelor ECTS la depunerea Learning Agreement | Timp de execuție a metodei de validare a invariantului | **Latență < 100 ms** | Test de unitate și integrare JUnit/JMH: invocarea `LearningAgreement.validateEctsBalance()` pe contracte cu până la 30 de linii curriculare (Table A / Table B). | Validare pură în memorie la nivelul Agregatului DDD fără operații I/O blocante sau interogări de rețea. |
| **NFR-03** | **Securitate & GDPR** | Jurnalizarea imuabilă a operațiunilor de audit pentru date personale și decizii | Rata de captură și latența de persistență | **100% din operațiuni capturate**, persistență sincronă în **< 20 ms** | Test de securitate: interceptarea oricărui eveniment de tip modificare notă, aprobare LA sau acces date PII (CNP, IBAN). Intrarea este persistată într-un tabel append-only semnat hash SHA-256. | Aspect-Oriented Programming (Spring AOP `@Audited`), tabel dedicat de audit imuabil, permisiuni restrictive DB. |
| **NFR-04** | **Scalabilitate & Procesare Asincronă** | Scanarea termenelor limită și expedierea reminderelor de scadență | Throughput procesare batch | **10.000 dosare procesate în < 60 secunde** | Test batch de noapte: rularea job-ului de evaluare a scadențelor pe o bază de date cu 10.000 de mobilități active, identificarea sarcinilor restante și expedierea alertelor. | Spring Batch / Scheduled Task paralelizat cu Virtual Threads (JDK 23), cozi dedicate de mesaje RabbitMQ. |
| **NFR-05** | **Consistență Tranzacțională** | Consistența stărilor la anularea mobilității (Interruptible Region) | Timp de propagare și convergență a stărilor | **Consistență atomică ACID** (tranzacție unică) sau convergență asincronă în **< 1.500 ms** | Test de integrare tranzacțională: la invocarea `CancelMobility`, starea agregatului `LearningAgreement` devine `Anulat`, iar toate sarcinile de checklist active devin `Anulat`/`Depasit`. | Modelul **Transactional Outbox**: persistența atomica a evenimentului `MobilityCancelledEvent` în tabela Outbox, urmată de consum idempotent. |
| **NFR-06** | **Disponibilitate** | Rata de funcționare a platformei în perioadele de vârf academic | Disponibilitate lunară (Uptime) | **Disponibilitate ≥ 99.5%** în lunile Septembrie-Octombrie și Februarie-Martie | Monitorizare Prometheus / Grafana pe endpoint-ul `/actuator/health` în condiții de sarcină normală și de vârf; MTTR < 15 minute. | Deployment containerizat Kubernetes, auto-scaling pe baza încărcării CPU/memorie, redundanță PostgreSQL Replica. |
| **NFR-07** | **Securitate & Autorizare** | Segregarea accesului bazat pe roluri (RBAC) | Rata de refuz a tentativelor neautorizate | **100% acces refuzat** (HTTP 403 Forbidden) pentru încercările de manipulare a contractelor altor studenți | Teste de securitate OWASP Top 10 (Broken Access Control) automatizate cu Spring Security Test. | Validare strictă a drepturilor de autorizat pe bază de JWT federat eduGAIN și verificarea identității `SecurityContext.getCurrentStudentId() == LA.getStudentId()`. |

