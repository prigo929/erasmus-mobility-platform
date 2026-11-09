"""
Generate the missing visual diagrams:
1. Figura 1: Strategic DDD Context Map (replaces raw Mermaid flowchart)
2. Figura 1b: Main Transaction Flow Sequence Diagram (replaces raw Mermaid sequence)
3. Figura 9b: Four-Layer Onion/Clean Architecture Conceptual Layers (replaces ASCII box diagram)
"""

from pathlib import Path
import subprocess

PNG_DIR = Path(__file__).resolve().parents[1] / "models/diagrams-png"
PNG_DIR.mkdir(parents=True, exist_ok=True)

def render_svg_to_png(svg_path, png_path):
    cmd = f"qlmanage -t -s 2000 -o '{PNG_DIR}' '{svg_path}'"
    subprocess.run(cmd, shell=True, check=True)
    generated = PNG_DIR / (svg_path.name + ".png")
    if generated.exists():
        if png_path.exists():
            png_path.unlink()
        generated.rename(png_path)
        print(f"Generated {png_path.name} ({png_path.stat().st_size} bytes)")

# ==============================================================================
# 1. FIGURA 1: Strategic DDD Context Map
# ==============================================================================
fig1_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 960" width="100%" height="100%" style="background-color: #FBF8F1; font-family: Roboto, -apple-system, BlinkMacSystemFont, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2D3748" />
    </marker>
    <marker id="outbox-arrow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <polygon points="0,2 10,6 0,10" fill="#9C4221" />
    </marker>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="2" dy="2" stdDeviation="2.5" flood-opacity="0.10" />
    </filter>
  </defs>

  <!-- Title -->
  <text x="40" y="38" font-size="20" font-weight="bold" fill="#1A202C">Figura 1. Strategic DDD Context Map (Bounded Contexts &amp; Integration Contracts)</text>
  <text x="40" y="60" font-size="12" fill="#5A4A3E">Erasmus Mobility Platform: Core vs. Supporting Subdomains, Shared Kernel &amp; Decoupled Integration Contracts</text>

  <!-- ==================== SUPPORTING SUBDOMAIN 1: Equivalence Management (Top Center) ==================== -->
  <g transform="translate(480, 90)">
    <rect x="0" y="0" width="440" height="150" rx="10" fill="#EBF4FF" stroke="#3182CE" stroke-width="1.8" filter="url(#shadow)" />
    <rect x="0" y="0" width="440" height="34" rx="10" fill="#3182CE" />
    <text x="220" y="22" text-anchor="middle" font-size="13" font-weight="bold" fill="#FFFFFF">Gestiunea Echivalărilor Academice (Supporting Subdomain)</text>
    <text x="20" y="58" font-size="11.5" font-weight="bold" fill="#2B6CB0">AcademicEquivalence (Aggregate Root)</text>
    <text x="20" y="76" font-size="10.5" fill="#2D3748">• CourseSyllabus (Value Object: tematici, credite, ore)</text>
    <text x="20" y="94" font-size="10.5" fill="#2D3748">• ValidityWindow (Value Object: interval calendaristic)</text>
    <text x="20" y="112" font-size="10.5" fill="#2D3748">• SyllabusEvaluationService (Domain Service: similitudine >= 80%)</text>
    <text x="20" y="132" font-size="10" font-style="italic" fill="#718096">Contract de expunere: REST Open Host Service (/api/v1/equivalences/verify)</text>
  </g>

  <!-- ==================== CORE DOMAIN: Learning Agreement Management (Center) ==================== -->
  <g transform="translate(450, 330)">
    <rect x="0" y="0" width="500" height="180" rx="10" fill="#FFF8EE" stroke="#8D5B4C" stroke-width="2.2" filter="url(#shadow)" />
    <rect x="0" y="0" width="500" height="36" rx="10" fill="#8D5B4C" />
    <text x="250" y="23" text-anchor="middle" font-size="14" font-weight="bold" fill="#FFFFFF">Managementul Contractelor de Studii (Core Domain)</text>
    <text x="20" y="62" font-size="12" font-weight="bold" fill="#9C4221">LearningAgreement (Aggregate Root)</text>
    <text x="20" y="82" font-size="11" fill="#2D3748">• CourseLineTableA (Internal Child Entity: materii universitate gazdă)</text>
    <text x="20" y="100" font-size="11" fill="#2D3748">• CourseLineTableB (Internal Child Entity: discipline echivalate acasă)</text>
    <text x="20" y="118" font-size="11" fill="#2D3748">• ECTSParityService (Domain Service: sum(TableA) == sum(TableB) >= 30)</text>
    <text x="20" y="138" font-size="10.5" font-weight="bold" fill="#2D3748">Tranzacție ACID locală:</text>
    <text x="20" y="156" font-size="10" fill="#7A583A">Salvare stare agregat + scriere LearningAgreementApprovedEvent în tabela Outbox</text>
  </g>

  <!-- ==================== SUPPORTING SUBDOMAIN 2: Mobility Preparation (Right Bottom) ==================== -->
  <g transform="translate(850, 600)">
    <rect x="0" y="0" width="480" height="170" rx="10" fill="#EBF8FF" stroke="#319795" stroke-width="1.8" filter="url(#shadow)" />
    <rect x="0" y="0" width="480" height="34" rx="10" fill="#319795" />
    <text x="240" y="22" text-anchor="middle" font-size="13" font-weight="bold" fill="#FFFFFF">Pregătirea Mobilității &amp; Onboarding (Supporting Subdomain)</text>
    <text x="20" y="58" font-size="11.5" font-weight="bold" fill="#234E52">MobilityChecklist (Aggregate Root)</text>
    <text x="20" y="76" font-size="10.5" fill="#2D3748">• ChecklistTask (Child Entity: sarcină administrativă individuală)</text>
    <text x="20" y="94" font-size="10.5" fill="#2D3748">• Invariant: areMandatoryTasksComplete() [Poarta de plecare fizică]</text>
    <text x="20" y="114" font-size="10.5" fill="#2D3748">• IProcessedEventRepository (Port de persistență: verificare idempotență)</text>
    <text x="20" y="134" font-size="10" font-style="italic" fill="#718096">Consumator asincron idempotent: NominationMessageReceiver</text>
  </g>

  <!-- ==================== SHARED KERNEL (Bottom Center) ==================== -->
  <g transform="translate(470, 780)">
    <rect x="0" y="0" width="460" height="120" rx="10" fill="#FEFCBF" stroke="#D69E2E" stroke-width="1.8" filter="url(#shadow)" />
    <rect x="0" y="0" width="460" height="30" rx="10" fill="#D69E2E" />
    <text x="230" y="20" text-anchor="middle" font-size="12" font-weight="bold" fill="#1A202C">«Shared Kernel» Tipuri Imutabile Comune</text>
    <text x="20" y="52" font-size="10.5" font-weight="bold" fill="#744210">• StudentId (Value Object: UUID)</text>
    <text x="20" y="70" font-size="10.5" font-weight="bold" fill="#744210">• AgreementId / ChecklistId / EquivalenceId (Value Objects)</text>
    <text x="20" y="88" font-size="10.5" font-weight="bold" fill="#744210">• AcademicPeriod (Value Object: endDate >= startDate)</text>
    <text x="20" y="106" font-size="10.5" font-weight="bold" fill="#744210">• ECTSCredits (Value Object: credite nenegative, prag minim 30)</text>
  </g>

  <!-- ==================== GENERIC SUBDOMAIN 1: Securitate & Audit GDPR (Left Bottom) ==================== -->
  <g transform="translate(50, 600)">
    <rect x="0" y="0" width="350" height="120" rx="10" fill="#EDF2F7" stroke="#718096" stroke-width="1.6" filter="url(#shadow)" />
    <rect x="0" y="0" width="350" height="30" rx="10" fill="#718096" />
    <text x="175" y="20" text-anchor="middle" font-size="12" font-weight="bold" fill="#FFFFFF">Securitate &amp; Audit GDPR (Generic)</text>
    <text x="15" y="52" font-size="10.5" fill="#2D3748">• Autentificare centralizată OAuth2 / EWP</text>
    <text x="15" y="70" font-size="10.5" fill="#2D3748">• Jurnal de audit append-only semnat HMAC SHA-256</text>
    <text x="15" y="88" font-size="10.5" fill="#2D3748">• Segregare acces PII (roluri Coordonator, Student, DRI)</text>
  </g>

  <!-- ==================== GENERIC SUBDOMAIN 2: Notificări & Alerte (Top Left) ==================== -->
  <g transform="translate(50, 100)">
    <rect x="0" y="0" width="350" height="110" rx="10" fill="#EDF2F7" stroke="#718096" stroke-width="1.6" filter="url(#shadow)" />
    <rect x="0" y="0" width="350" height="30" rx="10" fill="#718096" />
    <text x="175" y="20" text-anchor="middle" font-size="12" font-weight="bold" fill="#FFFFFF">Serviciul de Notificări &amp; Alerte (Generic)</text>
    <text x="15" y="52" font-size="10.5" fill="#2D3748">• Dispecer e-mail notificări scadențe</text>
    <text x="15" y="70" font-size="10.5" fill="#2D3748">• Remindere sarcină nesoluționată (after 5 days)</text>
    <text x="15" y="88" font-size="10.5" fill="#2D3748">• Notificări push pe portalul studentului</text>
  </g>

  <!-- ==================== INTEGRATION EDGES & LABELS ==================== -->
  <!-- 1. Core <-> Equivalence (Customer / Supplier via REST) -->
  <path d="M 660 330 L 660 245" fill="none" stroke="#2B6CB0" stroke-width="2" marker-end="url(#arrow)" />
  <rect x="670" y="265" width="220" height="42" rx="6" fill="#FFFFFF" stroke="#2B6CB0" stroke-width="1" />
  <text x="678" y="282" font-size="10" font-weight="bold" fill="#2B6CB0">Customer / Supplier (Sync REST)</text>
  <text x="678" y="296" font-size="9" fill="#2D3748">LA = Customer [D] / EQ = Supplier [U]</text>

  <!-- 2. Core -> Preparation (Domain Events via Transactional Outbox) -->
  <path d="M 850 510 L 970 600" fill="none" stroke="#C53030" stroke-width="2.4" stroke-dasharray="6,4" marker-end="url(#outbox-arrow)" />
  <rect x="880" y="535" width="230" height="42" rx="6" fill="#FFF5F5" stroke="#C53030" stroke-width="1" />
  <text x="888" y="552" font-size="10" font-weight="bold" fill="#C53030">Evenimente de Domeniu (Outbox)</text>
  <text x="888" y="566" font-size="9" fill="#2D3748">LearningAgreementApprovedEvent</text>

  <!-- 3. Core -> Shared Kernel -->
  <path d="M 700 510 L 700 775" fill="none" stroke="#B7791F" stroke-width="1.6" marker-end="url(#arrow)" />

  <!-- 4. Equivalence -> Shared Kernel (curved) -->
  <path d="M 910 240 C 1020 380 970 700 870 780" fill="none" stroke="#B7791F" stroke-width="1.4" stroke-dasharray="4,3" marker-end="url(#arrow)" />

  <!-- 5. Preparation -> Shared Kernel -->
  <path d="M 920 770 L 920 780" fill="none" stroke="#B7791F" stroke-width="1.6" marker-end="url(#arrow)" />

  <!-- 6. Generic Integrations -->
  <path d="M 450 400 L 250 215" fill="none" stroke="#718096" stroke-width="1.4" stroke-dasharray="4,3" marker-end="url(#arrow)" />
  <text x="270" y="300" font-size="9" fill="#4A5568">Alerte întârziere review</text>

  <path d="M 450 470 L 320 600" fill="none" stroke="#718096" stroke-width="1.4" stroke-dasharray="4,3" marker-end="url(#arrow)" />
  <text x="310" y="535" font-size="9" fill="#4A5568">Jurnalizare semnare contract</text>

  <!-- Explanatory note -->
  <g transform="translate(50, 800)">
    <rect x="0" y="0" width="370" height="85" rx="6" fill="#FFFFF0" stroke="#D69E2E" stroke-width="1" />
    <text x="12" y="20" font-size="9.5" font-weight="bold" fill="#744210">Notă Arhitecturală (Regula Shared Kernel):</text>
    <text x="12" y="38" font-size="9" fill="#2D3748">Nucleul partajat conține exclusiv tipuri imutabile de identitate</text>
    <text x="12" y="52" font-size="9" fill="#2D3748">și intervale/credite. Niciun context nu accesează direct tabelele</text>
    <text x="12" y="66" font-size="9" fill="#2D3748">altui subdomeniu; comunicarea este strict decuplată prin porturi.</text>
  </g>
</svg>'''

fig1_svg_path = PNG_DIR / "Figura1-Strategic-DDD-Context-Map.svg"
fig1_png_path = PNG_DIR / "Figura1-Strategic-DDD-Context-Map.png"
fig1_svg_path.write_text(fig1_svg, encoding="utf-8")
render_svg_to_png(fig1_svg_path, fig1_png_path)

# ==============================================================================
# 2. FIGURA 1b: Main Transaction Flow Sequence Diagram
# ==============================================================================
fig1b_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1300 900" width="100%" height="100%" style="background-color: #FBF8F1; font-family: Roboto, -apple-system, BlinkMacSystemFont, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2D3748" />
    </marker>
    <marker id="async-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <polygon points="0,2 9,5 0,8" fill="#C53030" />
    </marker>
  </defs>

  <!-- Title -->
  <text x="30" y="34" font-size="18" font-weight="bold" fill="#1A202C">Figura 1b. Diagrama de Secvență a Fluxului Tranzacțional Principal Cross-Subdomenii</text>
  <text x="30" y="52" font-size="11" fill="#5A4A3E">Etapele ciclului complet de mobilitate academică între cele trei contexte delimitate și actorii externi</text>

  <!-- Lifeline Headers -->
  <!-- 1. Student -->
  <rect x="40" y="70" width="120" height="35" rx="6" fill="#EDF2F7" stroke="#4A5568" />
  <text x="100" y="92" text-anchor="middle" font-size="11" font-weight="bold" fill="#2D3748">Student</text>
  <line x1="100" y1="105" x2="100" y2="860" stroke="#A0AEC0" stroke-width="1.2" stroke-dasharray="4,4" />

  <!-- 2. Home Coordinator -->
  <rect x="220" y="70" width="150" height="35" rx="6" fill="#EDF2F7" stroke="#4A5568" />
  <text x="295" y="92" text-anchor="middle" font-size="11" font-weight="bold" fill="#2D3748">Coordonator Acasă</text>
  <line x1="295" y1="105" x2="295" y2="860" stroke="#A0AEC0" stroke-width="1.2" stroke-dasharray="4,4" />

  <!-- 3. Mobility Preparation -->
  <rect x="430" y="70" width="170" height="35" rx="6" fill="#EBF8FF" stroke="#319795" />
  <text x="515" y="92" text-anchor="middle" font-size="11" font-weight="bold" fill="#234E52">Mobility Preparation</text>
  <line x1="515" y1="105" x2="515" y2="860" stroke="#319795" stroke-width="1.2" stroke-dasharray="4,4" />

  <!-- 4. Equivalence Management -->
  <rect x="660" y="70" width="170" height="35" rx="6" fill="#EBF4FF" stroke="#3182CE" />
  <text x="745" y="92" text-anchor="middle" font-size="11" font-weight="bold" fill="#2B6CB0">Equivalence Context</text>
  <line x1="745" y1="105" x2="745" y2="860" stroke="#3182CE" stroke-width="1.2" stroke-dasharray="4,4" />

  <!-- 5. Learning Agreement (Core) -->
  <rect x="890" y="70" width="180" height="35" rx="6" fill="#FFF8EE" stroke="#8D5B4C" />
  <text x="980" y="92" text-anchor="middle" font-size="11" font-weight="bold" fill="#9C4221">Learning Agreement</text>
  <line x1="980" y1="105" x2="980" y2="860" stroke="#8D5B4C" stroke-width="1.4" stroke-dasharray="4,4" />

  <!-- 6. Host Coordinator -->
  <rect x="1120" y="70" width="150" height="35" rx="6" fill="#EDF2F7" stroke="#4A5568" />
  <text x="1195" y="92" text-anchor="middle" font-size="11" font-weight="bold" fill="#2D3748">Coordonator Gazdă</text>
  <line x1="1195" y1="105" x2="1195" y2="860" stroke="#A0AEC0" stroke-width="1.2" stroke-dasharray="4,4" />

  <!-- STAGE 1 BANNER -->
  <rect x="40" y="120" width="1230" height="26" fill="#E2E8F0" rx="4" />
  <text x="50" y="138" font-size="11" font-weight="bold" fill="#2D3748">Etapa 1: Confirmare Nominalizare și Inițializare Dosar Administrativ (Mobility Preparation)</text>

  <line x1="295" y1="170" x2="515" y2="170" stroke="#2D3748" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="405" y="164" font-size="9.5" text-anchor="middle" fill="#2D3748">1. confirmNomination(StudentId, MobilityId)</text>

  <path d="M 515 185 C 555 185 555 210 515 210" fill="none" stroke="#2D3748" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="565" y="202" font-size="9" fill="#2D3748">2. initializeDefaultPreparationTasks()</text>

  <line x1="515" y1="230" x2="100" y2="230" stroke="#718096" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)" />
  <text x="307" y="224" font-size="9" fill="#4A5568">3. Notificare nominalizare activă + dosar checklist inițializat</text>

  <!-- STAGE 2 BANNER -->
  <rect x="40" y="260" width="1230" height="26" fill="#E2E8F0" rx="4" />
  <text x="50" y="278" font-size="11" font-weight="bold" fill="#2D3748">Etapa 2: Căutare în Catalogul de Echivalări și Validare Silabe (Equivalence Management)</text>

  <line x1="100" y1="310" x2="745" y2="310" stroke="#2D3748" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="422" y="304" font-size="9.5" text-anchor="middle" fill="#2D3748">4. GET /api/v1/equivalences/verify?sendCode=...&amp;hostCode=...</text>

  <line x1="745" y1="340" x2="100" y2="340" stroke="#718096" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)" />
  <text x="422" y="334" font-size="9" fill="#4A5568">5. Răspuns: Echivalare activă găsită (ECTS recunoscute, valabilitate)</text>

  <!-- STAGE 3 BANNER -->
  <rect x="40" y="375" width="1230" height="26" fill="#E2E8F0" rx="4" />
  <text x="50" y="393" font-size="11" font-weight="bold" fill="#2D3748">Etapa 3: Redactare Contract de Studii și Validare Invariant de Credite (Core Domain)</text>

  <line x1="100" y1="425" x2="980" y2="425" stroke="#2D3748" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="540" y="419" font-size="9.5" text-anchor="middle" fill="#2D3748">6. createDraft(StudentId, AcademicYear)</text>

  <line x1="100" y1="455" x2="980" y2="455" stroke="#2D3748" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="540" y="449" font-size="9.5" text-anchor="middle" fill="#2D3748">7. addTableALine(...) &amp; addTableBLine(...)</text>

  <line x1="100" y1="485" x2="980" y2="485" stroke="#2D3748" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="540" y="479" font-size="9.5" text-anchor="middle" font-weight="bold" fill="#2D3748">8. submit()</text>

  <path d="M 980 495 C 1020 495 1020 520 980 520" fill="none" stroke="#9C4221" stroke-width="1.6" marker-end="url(#arrow)" />
  <text x="1030" y="512" font-size="9" font-weight="bold" fill="#9C4221">9. hasCreditParity() [Σ A == Σ B >= 30]</text>

  <line x1="980" y1="540" x2="100" y2="540" stroke="#718096" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow)" />
  <text x="540" y="534" font-size="9" fill="#4A5568">10. 200 OK (Stare: SUBMITTED, linii blocate la editare)</text>

  <!-- STAGE 4 BANNER -->
  <rect x="40" y="570" width="1230" height="26" fill="#E2E8F0" rx="4" />
  <text x="50" y="588" font-size="11" font-weight="bold" fill="#2D3748">Etapa 4: Avizare Tripartită, Sincronizare Outbox și Deblocare Poartă de Plecare</text>

  <line x1="295" y1="620" x2="980" y2="620" stroke="#2D3748" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="637" y="614" font-size="9.5" text-anchor="middle" fill="#2D3748">11. approve(coordinatorId) [Stare: APPROVED_BY_FACULTY]</text>

  <line x1="980" y1="655" x2="1195" y2="655" stroke="#2D3748" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="1087" y="649" font-size="9.5" text-anchor="middle" fill="#2D3748">12. Transmitere către partener prin rețeaua EWP</text>

  <line x1="1195" y1="685" x2="980" y2="685" stroke="#2D3748" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="1087" y="679" font-size="9.5" text-anchor="middle" fill="#2D3748">13. confirmByHost(signatureRef) [Stare: CONFIRMED_BY_HOST]</text>

  <line x1="980" y1="725" x2="515" y2="725" stroke="#C53030" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#async-arrow)" />
  <text x="747" y="718" font-size="9.5" text-anchor="middle" font-weight="bold" fill="#C53030">14. Publicare asincronă Outbox: LearningAgreementApprovedEvent</text>

  <path d="M 515 745 C 555 745 555 770 515 770" fill="none" stroke="#234E52" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="565" y="762" font-size="9" fill="#234E52">15. completeTask(LA_COUNTERSIGN)</text>

  <path d="M 515 785 C 555 785 555 810 515 810" fill="none" stroke="#234E52" stroke-width="1.4" marker-end="url(#arrow)" />
  <text x="565" y="802" font-size="9" font-weight="bold" fill="#234E52">16. areMandatoryTasksComplete() == true -> CONFIRMED_READY</text>

  <line x1="515" y1="835" x2="100" y2="835" stroke="#234E52" stroke-width="1.4" stroke-dasharray="4,3" marker-end="url(#arrow)" />
  <text x="307" y="829" font-size="9" font-weight="bold" fill="#234E52">17. Deblocare tranșă grant financiar și autorizare plecare la studii</text>
</svg>'''

fig1b_svg_path = PNG_DIR / "Figura1b-Main-Transaction-Flow-Sequence.svg"
fig1b_png_path = PNG_DIR / "Figura1b-Main-Transaction-Flow-Sequence.png"
fig1b_svg_path.write_text(fig1b_svg, encoding="utf-8")
render_svg_to_png(fig1b_svg_path, fig1b_png_path)

# ==============================================================================
# 3. FIGURA 9b: Four-Layer Onion/Clean Architecture Conceptual Layers
# ==============================================================================
fig9b_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 700" width="100%" height="100%" style="background-color: #FBF8F1; font-family: Roboto, -apple-system, BlinkMacSystemFont, sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#2D3748" />
    </marker>
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="2" dy="2" stdDeviation="2.5" flood-opacity="0.10" />
    </filter>
  </defs>

  <!-- Title -->
  <text x="30" y="34" font-size="18" font-weight="bold" fill="#1A202C">Figura 9b. Arhitectura Conceptuală pe 4 Straturi DDD cu Inversarea Dependențelor (DIP)</text>
  <text x="30" y="52" font-size="11" fill="#5A4A3E">Separarea strictă a preocupărilor: Stratul Domain este complet decuplat de cadre tehnice și baze de date</text>

  <!-- Layer 1: Presentation (Top) -->
  <g transform="translate(100, 80)">
    <rect x="0" y="0" width="900" height="90" rx="8" fill="#EDF2F7" stroke="#4A5568" stroke-width="1.6" filter="url(#shadow)" />
    <text x="25" y="28" font-size="13" font-weight="bold" fill="#1A365D">1. User Interface &amp; Presentation Layer (Stratul de Prezentare)</text>
    <text x="25" y="50" font-size="10.5" fill="#2D3748">• Spring @RestController (LearningAgreementWebController, EquivalenceApiRest)</text>
    <text x="25" y="68" font-size="10.5" fill="#2D3748">• Validare request-uri HTTP, mapare DTO-uri &lt;-&gt; Command objects, serializare răspunsuri JSON</text>
  </g>

  <!-- Downward delegation arrow 1 -> 2 -->
  <line x1="550" y1="170" x2="550" y2="215" stroke="#2D3748" stroke-width="1.8" marker-end="url(#arrow)" />
  <text x="560" y="196" font-size="10" font-style="italic" fill="#718096">deleagă comanda</text>

  <!-- Layer 2: Application Layer -->
  <g transform="translate(100, 220)">
    <rect x="0" y="0" width="900" height="100" rx="8" fill="#EBF8FF" stroke="#3182CE" stroke-width="1.6" filter="url(#shadow)" />
    <text x="25" y="28" font-size="13" font-weight="bold" fill="#2B6CB0">2. Application Layer (Stratul de Aplicație / Orchestrate Use Cases)</text>
    <text x="25" y="50" font-size="10.5" fill="#2D3748">• Application Services (AgreementApplicationService, PreparationApplicationService)</text>
    <text x="25" y="68" font-size="10.5" fill="#2D3748">• Granițe tranzacționale declarative (@Transactional ACID), încărcare agregate din Repository</text>
    <text x="25" y="86" font-size="10.5" fill="#2D3748">• Dispecerizare comenzi, scriere în tabela Outbox, zero logică de afaceri în serviciu</text>
  </g>

  <!-- Downward invocation arrow 2 -> 3 -->
  <line x1="550" y1="320" x2="550" y2="365" stroke="#2D3748" stroke-width="1.8" marker-end="url(#arrow)" />
  <text x="560" y="346" font-size="10" font-style="italic" fill="#718096">1. încarcă / 2. invocă operații pe agregat / 3. salvează</text>

  <!-- Layer 3: Domain Layer (The Heart) -->
  <g transform="translate(100, 370)">
    <rect x="0" y="0" width="900" height="130" rx="8" fill="#FFF8EE" stroke="#8D5B4C" stroke-width="2.2" filter="url(#shadow)" />
    <text x="25" y="28" font-size="14" font-weight="bold" fill="#9C4221">3. Domain Layer (Inima Sistemului - DDD Core)</text>
    <text x="25" y="50" font-size="11" font-weight="bold" fill="#2D3748">• Agregate Rădăcină (LearningAgreement, AcademicEquivalence, MobilityChecklist)</text>
    <text x="25" y="68" font-size="10.5" fill="#2D3748">• Entități Interne Copil (CourseLineTableA, CourseLineTableB, ChecklistTask)</text>
    <text x="25" y="86" font-size="10.5" fill="#2D3748">• Value Objects Imutabile (StudentId, AgreementId, ECTSCredits, ValidityWindow)</text>
    <text x="25" y="104" font-size="10.5" fill="#2D3748">• Porturi de Persistență (Interfețe Domain Repositories) &amp; Evenimente de Domeniu</text>
    <text x="25" y="120" font-size="10" font-style="italic" fill="#7A583A">Complet decuplat: ZERO importuri tehnice de Spring, JPA, Hibernate, Jackson sau HTTP.</text>
  </g>

  <!-- Inverted arrow 4 -> 3 (Dependency Inversion Principle) -->
  <line x1="550" y1="540" x2="550" y2="505" stroke="#2D3748" stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrow)" />
  <text x="560" y="526" font-size="10" font-style="italic" fill="#718096">implementează porturile (DIP)</text>

  <!-- Layer 4: Infrastructure Layer -->
  <g transform="translate(100, 545)">
    <rect x="0" y="0" width="900" height="110" rx="8" fill="#F7FAFC" stroke="#718096" stroke-width="1.6" filter="url(#shadow)" />
    <text x="25" y="28" font-size="13" font-weight="bold" fill="#4A5568">4. Infrastructure Layer (Stratul de Infrastructură &amp; Persistență)</text>
    <text x="25" y="50" font-size="10.5" fill="#2D3748">• Implementări JPA/Hibernate (LearningAgreementRepoJPA extinde AbstractRepositoryJPA)</text>
    <text x="25" y="68" font-size="10.5" fill="#2D3748">• Adaptori REST Client (EquivalenceRestAdapter) pentru integrarea sincronă HTTP</text>
    <text x="25" y="86" font-size="10.5" fill="#2D3748">• Broker de Mesaje &amp; Scheduler Outbox (OutboxDispatcher, AgreementApprovedMessageReceiver)</text>
  </g>
</svg>'''

fig9b_svg_path = PNG_DIR / "Figura9b-Layered-Architecture-Conceptual-Layers.svg"
fig9b_png_path = PNG_DIR / "Figura9b-Layered-Architecture-Conceptual-Layers.png"
fig9b_svg_path.write_text(fig9b_svg, encoding="utf-8")
render_svg_to_png(fig9b_svg_path, fig9b_png_path)

print("All missing visual diagrams generated successfully!")

