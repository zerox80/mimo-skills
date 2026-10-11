---
name: deep-security-scan
description: "Perform several source-backed audit passes over the same supplied repository or scoped paths to challenge findings and improve coverage. Use for a deep, exhaustive, multi-pass, or variance-reducing security audit, deep scan, thorough repository-wide review, or tiefes/mehrdurchläufiges Security-Audit. Not for a PR, commit or patch review (use security-diff-scan) or a single-pass scan (use security-scan)."
---

<!-- Modified for MiMo Code on 2026-10-07. Derived from openai/codex-security at eb73cc0fa64f25f432bace6f8ff3f475038bfc71. Local workflows replace Codex host integration. See NOTICE and LICENSE. Extended with binding/validate scripts, pass playbooks, finding-family sinks and a hard consistency gate. -->

# Deep security scan

Read [references/mimo-runtime.md](references/mimo-runtime.md) for the actual tools, source-access limits and authorization boundaries in this MiMo Code session.

This is a local multi-pass audit. It does not reproduce the native Codex coordinator, parallel scan isolation, restart recovery, long-running background execution or usage accounting.

**Hard rules (never skip):**

1. Bind one source state and reuse it for every pass. Stop on drift; never merge two states.
2. Keep source read-only and the scan offline. Do not execute application code, install tools, or write tracker items.
3. `findings.json` is the source of truth. `report.md` may contain only those `F*` ids — never resurrect disproven candidates.
4. Every candidate gets one terminal outcome. Pending candidates never enter `findings[]`.
5. Do not claim statistical independence, sealed artifacts, SARIF, Codex-native scans, or token metering the environment did not provide.
6. Run `scripts/validate_artifacts.py` before delivery and fix every ERROR.

Bind one supplied source state and scope for every pass. Read [references/core-scan.md](references/core-scan.md), [references/multipass-orchestration.md](references/multipass-orchestration.md), [references/pass-playbooks.md](references/pass-playbooks.md) and [references/scan-artifacts.md](references/scan-artifacts.md). Honor the user's pass count or budget. If neither is specified, plan three bounded passes and state that assumption. Do not invent a fixed runtime or guaranteed coverage.

## Instructions

### Step 1: Bind the target

Resolve the exact repository or scoped paths, the inspected source state (revision, worktree dirtiness, snapshot identity), submodules, exclusions, optional reportability filter (e.g. bug-bounty program rules), output location and any user context. Reuse that identity for every pass. Never silently replace a different source state with the original target.

When a writable session is available, capture the binding with:

```bash
python scripts/bind_source.py <target> [--scope P ...] [--exclude P ...] --out <output-dir>/binding.json
```

Record the binding as a Task if the session has the Task tool, then start it. Keep pass-level progress in the scan output directory, not only in chat.

### Step 2: Plan the passes

Honor the user's pass count or budget. Default to three bounded passes and say so. Assign each pass a distinct substantive perspective before it starts, using the playbooks:

1. **Baseline:** architecture map, entrypoint inventory, forward traces, credential sweep, first candidates with counterevidence.
2. **Challenge:** backward traces, authorization/business logic, sibling entrypoints, sink variants, mandatory disposition of every pass-1 candidate (`keep` / `revise` / `disprove`).
3. **Proof gaps:** close remaining proof gaps, test strongest benign explanations, validate survivors, reconcile coverage.
4. **N+:** unused angle (supply chain, crypto, parsers, concurrency, multi-tenant, errors/logging, deployment) with a new-work claim.

State whether passes will share a context. Do not claim statistical independence or quantified variance reduction for sequential passes in one context.

### Step 3: Run the passes

Follow [references/multipass-orchestration.md](references/multipass-orchestration.md). Prefer real independent passes when MiMo's Actor tool can spawn subagents and the user has authorized delegation. Use the actor spawn brief template there. Give each pass the same bound source identity and scope, a distinct perspective brief, and the instruction to return candidates, covered paths, supporting paths, exclusions, unresolved gaps and a new-work claim. A second pass in the same context is not independent validation.

If Actor delegation is unavailable or unauthorized, run the passes sequentially in this context and say so explicitly. Use the Task tool to track pass completion when available.

For each pass, follow [references/core-scan.md](references/core-scan.md) and the matching playbook. Use [references/finding-families.md](references/finding-families.md) for sink catalogs. Keep source read-only and the scan offline. Do not execute application code, install tools or make tracker writes as part of the static audit.

### Step 4: Reconcile and deliver

Merge by the same broken control and effective remediation, preserving every independently affected instance. Do not add overlapping file counts across passes. Deduplicate covered paths. Apply the ID scheme in [references/report-templates.md](references/report-templates.md).

Every candidate gets exactly one outcome: `reportable`, `suppressed`, `not_applicable`, `disproven`/`disproven_as_reportable`, or `deferred` (`DEF-*`). Pending candidates never enter the validated findings array. An empty findings array means no validated finding in the reviewed material; it never establishes full coverage.

Save the aggregate local artifacts per [references/scan-artifacts.md](references/scan-artifacts.md) and [references/artifact-storage.md](references/artifact-storage.md). Record passes planned and completed. Report partial deep coverage if the requested passes or source review were unfinished, along with the retained findings and exact outstanding work.

**Consistency gate** — before you tell the user the scan is done:

```bash
python scripts/validate_artifacts.py <output-dir>
```

Fix every ERROR (report/findings divergence, resurrected disproven ids, dirty coverage paths, incomplete marked complete). Re-run until PASS.

## Examples

**User:** `/deep-security-scan` on this repository  
**Result:** Bind the current checkout (`bind_source.py`). Plan three passes (stated assumption). Run baseline, challenge and proof-gap passes. Deliver `report.md`, `findings.json`, `coverage.json`, `threatmodel.md` and `scan-manifest.json` with honest pass counts. `validate_artifacts.py` exits 0.

**User:** "Mach einen tiefen multi-pass Security-Audit über `src/` mit 4 Pässen"  
**Result:** Bind `src/` only. Plan four passes. Use four distinct perspectives (baseline, challenge, proof gaps, plus one rotating angle). Report coverage of `src/` only.

**User:** "Deep scan, but only offline and don't touch my worktree"  
**Result:** Read-only, offline. If artifacts cannot be written in the active mode, return supported results inline and identify unwritten artifacts.

**User:** "Deep scan with YesWeHack bug-bounty filter"  
**Result:** Record the program filter in `scan-manifest.scope`. Still discover broadly, but mark `in_scope: false` / suppress out-of-program families with reasons instead of dropping evidence silently.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Pass 2 just repeats Pass 1 | Same perspective reused | Force a different lens (forward, backward, authorization, open-ended) and require a new-work claim with newly opened paths |
| Coverage claims look inflated | Paths counted per pass or annotations in paths | Deduplicate across passes; clean repo-relative paths; count only fully reviewed inventory files |
| `report.md` lists findings that `findings.json` lacks | Draft/resurrected candidates | `findings.json` wins. Move disproven ids to coverage `suppressed_candidates` with `was_drafted_as` |
| `validate_artifacts.py` FAIL on id mismatch | Report written independently of findings | Generate the report findings table from `findings.json` only |
| Actor spawn denied or unavailable | Delegation not authorized | Fall back to sequential passes and disclose shared context |
| Mode cannot write files | Plan mode or restricted permissions | Return results inline, list unwritten artifacts, do not switch modes |
| Source changed mid-scan | Unbound checkout | Stop, rebind, or report drift; never merge results from two source states |
| Candidate keeps coming back after disproof | Sticky-id violation | Keep the `CAND-` id with `outcome: disproven`; revive only as a new candidate with a fresh proof |
| Gates left unresolved | Static audit cannot test external policy | Keep `status: reportable_with_gate` and `DEF-*` with `how_to_resolve`; never invent the gate result |
| Inventory too large to review | Scope too broad or missing exclusions | Narrow scope with the user, or deliver explicit partial coverage with `complete: false` |

## Important

- Keep discovery, validation and attack-path reasoning inside this audit. Phase skills are optional standalone workflows, not dependencies.
- Never claim a native Codex scan, sealed artifacts, a native scan database, SARIF export or measured token usage that the current environment did not provide.
- Installing a skill does not establish that any software is secure.
- `scripts/` are local helpers: read-only against the target, stdlib-only, offline. They validate structure and consistency, not factual correctness of findings.
