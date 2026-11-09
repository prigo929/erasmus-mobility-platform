# ErasmusModel XMI export

`ErasmusModel.xmi` is generated from Figures 16–18 in `docs/diagrams` with:

```bash
python3 tools/export_xmi.py
```

It contains the three bounded contexts, their presentation/application/domain/infrastructure packages, classes, interfaces, enumerations, attributes, operations, and diagram relationships. Import it into a new Enterprise Architect repository using **Import Model from XMI**, then inspect the imported packages and associations. Enterprise Architect may require an export from its own XMI dialect for round-trip fidelity; this standards-based file has not been tested in Enterprise Architect here. Diagram layout and the other diagram types are not included in this class-model export.

The Java P1 domain skeleton can be regenerated with `python3 tools/generate_domain.py`. Run `mvn clean compile` from `src/` with JDK 23 and Maven. The 30 generated source files compiled successfully with JDK 23 and Maven 3.8.7 on 2026-11-09.
