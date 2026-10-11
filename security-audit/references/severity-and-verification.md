# Severity & Verification Reference

## Severity scale (P1 / P2 / P3 only)

Only these three levels exist in this skill. Do **not** invent P0/P4/CRITICAL/INFO.

| Level | Name | Meaning | Typical impact | Default action |
|-------|------|---------|----------------|----------------|
| **P1** | High | Directly exploitable or one step from full compromise on a reachable path | Auth bypass, RCE, SQLi, SSRF to internal, secret leak of live credentials, unsafe deserialization | Fix before merge / hotfix |
| **P2** | Medium | Exploitable under specific conditions, limited blast radius, or defense-in-depth failure | XSS (reflected/stored with constraints), CSRF on state-changing ops, path traversal with partial control, weak crypto in non-critical path, hardcoded non-secret config that enables abuse | Fix in current sprint |
| **P3** | Low | Best-practice gap, hardening miss, or issue that needs many other failures first | Missing security headers, verbose errors, outdated dep without known exploit, missing rate limit on non-sensitive endpoint, weak input validation that is not directly exploitable | Backlog / hardening |

### Mapping rules

1. If severity is unclear between two levels, **choose the higher one**, then justify.
2. If a finding would be P0/critical in another scheme (unauthenticated RCE, full DB dump), **report it as P1** — this skill has no P0.
3. Informational notes, style, and pure performance issues are **out of scope**. Drop them.
4. The same root cause in multiple files = **one finding** with a file list, not N findings.
5. Do not pad the report. Zero findings is a valid outcome.

## Finding record (required fields)

Every accepted finding must carry:

```
id:        SA-001 (sequential)
severity:  P1 | P2 | P3
title:     short imperative summary
file:      path:line (and extra paths if same root cause)
category:  injection | auth | secrets | crypto | ssrf | xss | path-traversal |
           deserialization | access-control | config | dependency | other
evidence:  exact snippet or literal code quote that proves the issue
impact:    what an attacker can do
recommendation: concrete fix
confidence: confirmed | probable   (only after verification passes)
```

## Multi-pass verification (max 3 passes)

Goal: false positives are worse than missed cosmetic issues. Re-check every candidate finding until it is confirmed or dropped.

### Pass 1 — Source confirm
- Re-read the cited file at the cited lines (not from memory).
- The quoted `evidence` must appear in the file as claimed.
- Confirm the issue is in a **code file** and the path is **not** under a `.`-prefixed directory.
- Drop if: evidence mismatch, wrong file type, wrong path.

### Pass 2 — Exploitability / reachability
- Trace who calls this code. Is the dangerous input attacker-controlled?
- Check for existing sanitization, auth checks, or framework auto-escaping on that path.
- Re-check severity against the table above.
- Drop or downgrade if: input is not attacker-controlled, or a guard already covers it.

### Pass 3 — Counter-argument (adversarial)
- Write the strongest reason this is a **false positive**.
- If that counter-argument holds, drop the finding.
- If it does not hold, mark `confidence: confirmed`.
- If still ambiguous after pass 3, mark `confidence: probable` and keep only if severity is P1 or P2. Drop ambiguous P3s.

**Hard cap:** never run more than 3 verification passes. If unresolved after pass 3, the pass-3 rule decides (keep P1/P2 as `probable`, drop the rest). Do not loop forever.

### Per-finding log (keep in the report appendix)

```
SA-001  pass1: source OK  pass2: reachable via POST /login  pass3: no auto-escape -> CONFIRMED P1
SA-002  pass1: source OK  pass2: input not attacker-controlled -> DROPPED
SA-003  pass1: source OK  pass2: severity P3  pass3: ambiguous -> DROPPED
```

## Scope checklist (hard filters)

| Rule | Action |
|------|--------|
| Only code files | Use `scripts/list_code_files.py` allowlist |
| Skip dirs starting with `.` | Never walk into `.git`, `.venv`, `.idea`, etc. |
| Skip non-code | No Markdown, no images, no lockfiles as primary targets |
| Scope = project root unless user says otherwise | If user passes a path, audit only that path |
| Read-only | The audit never mutates project files |

## Out of scope for this skill

- Penetration testing, exploitation, payload generation, or writing exploit PoCs
- Infrastructure scanning of live hosts
- Dependency CVE databases (unless the user provides data)
- Findings only in docs, tests fixtures, or example code (report separately as P3 at most, or skip)
