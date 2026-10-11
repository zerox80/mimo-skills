# Report templates and ID scheme

Use these shapes for consistent, reconcilable output. [scan-artifacts.md](scan-artifacts.md) owns the artifact contract; this file shows concrete field values and prose structure. Run `scripts/validate_artifacts.py` before delivery.

## ID scheme

| Kind | Pattern | Example | Where it lives |
|---|---|---|---|
| Validated finding | `F` + integer, stable across passes | `F1` | `findings.json`, `report.md` |
| Candidate (any stage) | `CAND-` + SCREAMING-KEBAB of the issue | `CAND-OAUTH-NO-STATE` | candidate ledger, then `coverage.json` if not reportable |
| Deferred proof gap | `DEF-` + SCREAMING-KEBAB of the question | `DEF-SERVER-FILE-NAME-POLICY` | `coverage.json` → `deferred` |
| Finding gate | `G` + integer, scoped to a finding | `F1.gates[0].gate_id = "G1"` | `findings.json` |
| Pass artifact (optional) | `pass-<n>-<slug>.json` | `pass-2-challenge.json` | output dir, before merge |

Rules:

- IDs are stable once assigned. Renumbering invalidates cross-references.
- A candidate that is disproven keeps its `CAND-` id and moves to `coverage.suppressed_candidates` with `outcome: disproven`. It **must not** become an `F*` or reappear in `report.md` findings tables.
- If a draft finding is later disproven, record `was_drafted_as: "F2"` on the candidate and remove `F2` from `findings.json`. Never leave both.

## findings.json (excerpt)

```json
{
  "format": "mimo-security-scan/v1",
  "findings": [
    {
      "id": "F1",
      "title": "Path traversal via server-controlled filenames on offline cache paths",
      "severity": "low",
      "confidence": "medium",
      "category": ["path-traversal"],
      "cwe": "CWE-22",
      "weakness": "File(parent, name) joins remote name without rejecting '/' or '..'",
      "attacker": "Public-share visitor or shared-folder collaborator",
      "controlled_input": "Remote file/folder name",
      "prerequisites": ["API accepts '/' or '..' in names (gate G1)"],
      "violated_invariant": "Local paths stay under the intended cache root",
      "impact": "Write attacker bytes to app-private paths; possible FileProvider re-exposure",
      "counterevidence": "getCacheFile uses id-based paths; sandbox bounds the write",
      "remediation": "Reject '/' '..' '.' in remote names; canonicalize and assert root containment",
      "reportable": true,
      "status": "reportable_with_gate",
      "locations": [
        {
          "path": "app/src/main/java/example/File.kt",
          "startLine": 299,
          "endLine": 311,
          "roles": ["sink"],
          "symbol": "getOfflineFile()",
          "detail": "IOFile(folder, name) with remote name"
        }
      ],
      "evidence": [
        "File.kt:310 — `return if (isFolder()) folder else IOFile(folder, name)`"
      ],
      "gates": [
        {
          "gate_id": "G1",
          "description": "Does the API accept '/' or '..' in names?",
          "why_it_matters": "Determines whether the supply chain exists",
          "how_to_resolve": "Live create/rename test"
        }
      ]
    }
  ],
  "summary": {
    "total_findings": 1,
    "reportable": 1,
    "by_severity": { "critical": 0, "high": 0, "medium": 0, "low": 1, "info": 0 }
  }
}
```

## coverage.json (excerpt)

```json
{
  "format": "mimo-security-scan/v1",
  "requested_inventory": { "generated_from": "scripts/bind_source.py", "file_count": 412 },
  "fully_reviewed_paths": ["app/src/main/java/example/File.kt"],
  "supporting_paths": ["app/src/main/java/example/DownloadManagerUtils.kt"],
  "remaining_paths": ["app/src/test/**"],
  "exclusions": [{ "path": "docs/", "reason": "user-scoped out" }],
  "suppressed_candidates": [
    {
      "id": "CAND-LOGIN-CSRF-EXTERNAL-CODE",
      "title": "Login CSRF via external scheme callback",
      "outcome": "disproven",
      "reason": "Handler is not exported; callback path is dead code",
      "counterevidence": "WebViewLoginActivity.kt:35-43",
      "was_drafted_as": "F2"
    }
  ],
  "deferred": [
    {
      "id": "DEF-SERVER-FILE-NAME-POLICY",
      "title": "API filename policy for '/' and '..'",
      "why": "F1 exploitability",
      "how_to_resolve": "Live create/rename test with program User-Agent"
    }
  ],
  "open_questions": ["Does getRemotePath ever see multi-segment names?"],
  "complete": false
}
```

## report.md structure

```markdown
# <target> — Deep security scan

- **Target:** ...
- **Revision:** ... (clean / dirty)
- **Scope:** ... (include/exclude, program filter if any)
- **Method:** static source audit, N bounded passes (list perspectives). Offline; no live traffic.
- **Marker:** `mimo-security-scan/v1`

## Summary

<2–4 sentences: what was reviewed, how many findings, the dominant issue, and what was disproven.>

| ID | Severity | Title | Confidence |
|----|----------|-------|------------|
| F1 | Low | ... | Medium |

## F1 — <title>

**Severity:** ... **Confidence:** ...
**Prerequisites / gates:** ...

### Where
| # | Role | Location |
|---|------|----------|
| 1 | sink | `path:startLine` — detail |

### Attack
<numbered scenario with a concrete attacker>

### Impact
<concrete capability gain>

### Evidence
<quoted source with path:line>

### Counterevidence and gates
<what weakens the claim; what must be checked externally>

### Remediation
<practical fix at the broken control>

---

## Suppressed and disproven candidates

| ID | Outcome | Why |
|----|---------|-----|
| CAND-... | disproven | ... |

## Coverage

- Inventory: N files bound; fully reviewed: A; supporting: B; remaining: C; excluded: D.
- Passes: planned P, completed Q, independence: yes/no.
- `complete`: true/false — if false, exact remaining work.

## Next actions
<resolve gates / deferred items / remaining paths>
```

### Consistency rules (hard)

1. `findings.json` is the source of truth for what is a finding.
2. `report.md` findings table and detailed sections must contain **exactly** the `F*` ids in `findings.json` — no more, no less.
3. Disproven drafts appear only under Suppressed, as `CAND-*` (with `was_drafted_as` if they were once `F*`).
4. Empty `findings[]` means no validated finding in reviewed material — never "the repo is secure".
5. Severity and confidence are separate fields; never collapse them into one label.
6. Every location path is repository-relative without trailing annotations.

## scan-manifest.json (excerpt)

```json
{
  "format": "mimo-security-scan/v1",
  "target": {
    "name": "android-kDrive",
    "path": "/home/user/android-kDrive",
    "revision": "2fa0ff7...",
    "clean_tree": true,
    "submodules": []
  },
  "scan": {
    "skill": "deep-security-scan",
    "mode": "offline-source-audit",
    "passes_planned": 3,
    "passes_executed": 3,
    "pass_independence": false,
    "pass_independence_note": "Passes shared this session context and ran sequentially.",
    "live_traffic": false,
    "dynamic_testing": false
  },
  "scope": { "filter": "bug-bounty-relevant-only", "exclusions_applied": ["..."] },
  "source_limitations": ["..."],
  "performed_checks": ["..."],
  "outcome": {
    "reportable_findings": 1,
    "by_severity": { "critical": 0, "high": 0, "medium": 0, "low": 1, "info": 0 },
    "disproven_during_challenge": ["CAND-... (was drafted as F2) — reason"]
  },
  "artifacts": [
    "scan-manifest.json", "threatmodel.md", "findings.json", "coverage.json", "report.md"
  ]
}
```
