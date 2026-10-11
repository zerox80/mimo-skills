---
name: security-audit
description: Code-only security audit of a repository with severity levels P1, P2, and P3 only. Scans all code files, skips every folder starting with a dot, and re-verifies each finding up to 3 times before reporting. Use when the user asks for a "security audit", "Sicherheitsaudit", "code security review", "scan for vulnerabilities", "find security issues in this codebase", or wants P1/P2/P3 security findings. Do NOT use for live pentesting, exploit development, infrastructure scans of running hosts, or non-code content review.
---

# Security Audit

Read-only static security review of **code files** in a repository. Findings are limited to **P1 / P2 / P3** and must survive up to **3 verification passes** before they appear in the report.

## Hard rules (never break)

1. **Code files only** — discover them with `scripts/list_code_files.py`. Do not audit Markdown, images, binaries, or lockfiles as primary targets.
2. **Skip every directory whose name starts with `.`** — e.g. `.git`, `.venv`, `.idea`, `.github`. Never walk into them.
3. **Severity is only P1, P2, or P3** — no P0, no CRITICAL, no INFO. See `references/severity-and-verification.md`.
4. **Verify every candidate finding at most 3 times** (passes 1–3). After pass 3, accept as `confirmed` / `probable` or drop. Never loop beyond 3.
5. **Read-only** — do not modify project files during the audit.
6. **Do not write exploits or attack payloads.** Report the issue and the fix; do not produce working attack code.

## Workflow

### Step 1: Scope

- Default root = current working directory.
- If the user named a path, audit only that path (still skipping `.`-directories).
- Announce scope in one sentence: root, expected language mix, and that only code files are in scope.

### Step 2: Inventory code files

```bash
python scripts/list_code_files.py --json <ROOT>
```

- Store the JSON list. Every later finding must reference a file from this list.
- If the list is empty: stop and report "no code files in scope".
- If the list is huge (> ~400 files): audit in batches by directory, same rules per batch.

### Step 3: First-pass review (find candidates)

Read the inventoried files and look for issues in these categories:

| Category | Typical signals |
|----------|-----------------|
| injection | SQL/NoSQL/OS/LDAP built via string concat, `eval`, `exec`, shell=True, unsafe format strings |
| auth | missing authz on privileged routes, predictable tokens, JWT `verify=False` / alg=none, session fixation |
| secrets | API keys, passwords, private keys, connection strings in source |
| crypto | MD5/SHA1 for security, ECB mode, hardcoded IVs, weak RNG for tokens |
| ssrf | user-controlled URL fetched server-side without allowlist |
| xss | unescaped HTML injection, `dangerouslySetInnerHTML`, `innerHTML =`, `| safe` |
| path-traversal | user path joined into filesystem ops without normalization checks |
| deserialization | pickle/yaml.load/ObjectInputStream/PHP unserialize on untrusted input |
| access-control | IDOR patterns, missing object-level checks, CORS `*` with credentials |
| config | debug mode on in prod paths, permissive defaults, missing security headers in response builders |
| dependency | known-dangerous APIs of vendored libs, pinned to yanked versions if visible in code |

For each candidate, record a **finding record** (fields in `references/severity-and-verification.md`). Do not assign final severity yet — use a provisional level, then verify.

### Step 4: Verification (mandatory, max 3 passes)

Follow `references/severity-and-verification.md` → "Multi-pass verification":

1. **Pass 1 — Source confirm**: re-read the exact file:lines; evidence must match; path must pass the scope filters. Drop mismatches.
2. **Pass 2 — Exploitability**: is input attacker-controlled? Any guards/sanitizers/framework escaping? Adjust or drop severity.
3. **Pass 3 — Counter-argument**: write the strongest false-positive case. Keep only what survives.

Stop after pass 3. Apply the drop/keep rule for anything still ambiguous.

Keep a short per-finding verification log for the report appendix.

### Step 5: Report

Output a Markdown report in this order:

```markdown
# Security Audit — <root>

## Summary
- Files in scope: N
- Candidates: N
- Confirmed findings: N (P1: a, P2: b, P3: c)
- Dropped after verification: N

## Findings
### [P1] SA-001 Title
- file: path:line
- category: ...
- evidence: "quoted code"
- impact: ...
- recommendation: ...
- confidence: confirmed | probable

(... more findings, sorted P1 → P2 → P3, then by file)

## Dropped candidates
| id | reason | pass |
|----|--------|------|

## Verification log
SA-001 pass1: ... pass2: ... pass3: ...
```

Empty findings section is fine — say so explicitly in the Summary.

## Examples

**User:** "Mach ein Security Audit von diesem Repo"
→ Step 1–5 on cwd. Report with only P1–P3, only code files, verified findings.

**User:** "Scan src/ for security issues, P1-P2 only if possible"
→ Scope = `src/`. Still run all 3 verification passes. If the user narrows severity further, honor it on top of the P1–P3 rule.

**User:** "Audit the auth module for injection"
→ Scope = that path, categories filtered to injection + auth. Same verification.

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `list_code_files.py` finds nothing | empty repo, only docs, or everything under `.` dirs | Confirm root; if only docs exist, report out of scope |
| Finding cites `.venv/...` or `.git/...` | scope filter violated | Drop the finding; it is out of scope |
| Severity reported as CRITICAL/P0/P4 | wrong scale | Map to P1 (or lower); only P1/P2/P3 exist |
| Same issue many times | copied pattern | Merge into one finding with a file list |
| Verification still "maybe" after pass 3 | unresolved ambiguity | Keep as `probable` only if P1/P2; drop otherwise |
| Huge codebase, context limits | > ~400 files | Batch by top-level directory; apply the same rules per batch; merge the final report |

## Reference

Before classifying severity or finishing verification, read `references/severity-and-verification.md`.
