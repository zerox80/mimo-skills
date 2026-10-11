# Report Template

## Mandatory Finding Format

Use this format for every **CONFIRMED** finding. Apply the same fields to LIKELY/UNCONFIRMED entries in section 4 with their actual status.

```markdown
### Finding ID: SEC-001

| Field | Value |
|-------|-------|
| **Severity** | P0 / P1 / P2 |
| **Status** | CONFIRMED / LIKELY / UNCONFIRMED |
| **Title** | Concise vulnerability description |
| **CWE** | CWE-xxx (if applicable) |
| **Affected File** | Exact repository-relative path |
| **Lines** | Verified line number or range |
| **Root Cause** | Explanation of the security failure |
| **Entry Point** | Attacker-controlled input or interface |
| **Execution Path** | Source-to-sink flow through affected components |
| **Exploitability** | How the issue can realistically be exploited |
| **Prerequisites** | Required privileges and conditions |
| **Existing Defenses** | Why relevant safeguards are insufficient |
| **Security Impact** | Confidentiality, integrity, or availability consequences |
| **Severity Justification** | Evidence supporting the assigned priority |
| **Validation Pass 1** | Findings and evidence |
| **Validation Pass 2** | Independent verification results, if performed |
| **Validation Pass 3** | Final verification results, if performed |
| **Validation Count** | 1, 2, or 3 |
| **Recommended Fix** | Specific actionable remediation |
| **Residual Uncertainty** | Any remaining limitations |
```

**Do not fabricate line numbers, code snippets, test outcomes, or security impact.**

---

## Final Security Report Structure

The report language is **German**. Keep code identifiers, file paths, CWE IDs, and severity labels (P0/P1/P2) in their technical form.

---

### 1. Executive Summary (Zusammenfassung)

Provide:

- Overall audit assessment (Gesamtbewertung)
- Confirmed P0 count
- Confirmed P1 count
- Confirmed P2 count
- Likely findings count
- Unconfirmed findings count
- Most significant security risks (Wesentliche Risiken)

### 2. Repository Coverage (Abdeckung des Repositories)

Show:

- Reviewed components (Überprüfte Komponenten)
- Reviewed security boundaries (Überprüfte Sicherheitsgrenzen)
- Partially reviewed components (Teilweise überprüfte Komponenten)
- Excluded components with reason (Ausgeschlossene Komponenten)
- Inaccessible components (Nicht zugängliche Komponenten)
- Important audit limitations (Wesentliche Einschränkungen)

Use the coverage statuses: REVIEWED, PARTIALLY REVIEWED, EXCLUDED WITH REASON, INACCESSIBLE.

### 3. Confirmed Vulnerabilities (Bestätigte Schwachstellen)

Sort findings strictly by severity:

1. P0
2. P1
3. P2

For each confirmed vulnerability, include the full mandatory finding format above.

### 4. Likely and Unconfirmed Vulnerabilities (Wahrscheinliche und unbestätigte Schwachstellen)

Keep these separate from confirmed results.

Explain:

- Why they could not be confirmed
- Which evidence would resolve the uncertainty

### 5. Rejected False Positives (Verworfene Falschpositive)

Briefly document meaningful rejected candidates and the reasons for rejection.

### 6. Remediation Priority (Priorisierte Maßnahmen)

Provide a prioritized remediation order based on:

- Severity
- Realistic risk
- Affected functionality

### 7. Final Security Assessment (Abschließende Sicherheitsbewertung)

Summarize:

- What was verified
- What remains uncertain
- Important security boundaries
- Coverage limitations
- The highest-priority next steps

**Never state that the repository is completely secure simply because no vulnerabilities were found.**

---

## German terminology reference

| English | German |
|---------|--------|
| Security audit | Sicherheitsaudit |
| Vulnerability | Schwachstelle |
| Confirmed | Bestätigt |
| Likely | Wahrscheinlich |
| Unconfirmed | Unbestätigt |
| Rejected / False positive | Verworfen / Falschpositiv |
| Severity | Schweregrad |
| Remediation | Maßnahme / Behebung |
| Attack path | Angriffspfad |
| Impact | Auswirkung |
| Coverage | Abdeckung |
| Prerequisites | Voraussetzungen |
| Root cause | Ursache |
| Entry point | Einstiegspunkt |
| Security impact | Sicherheitsauswirkung |
| Residual uncertainty | Verbleibende Unsicherheit |
| Authorization | Autorisierung |
| Authentication | Authentifizierung |
| Privilege escalation | Rechteerhöhung |
| Remote code execution | Fernausführung von Code |
| Data exposure | Datenoffenlegung |
| Trust boundary | Vertrauensgrenze |
