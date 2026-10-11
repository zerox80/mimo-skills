<!-- Modified for MiMo Code on 2026-10-07. Derived from openai/codex-security at eb73cc0fa64f25f432bace6f8ff3f475038bfc71. Local workflows replace Codex host integration. See NOTICE and LICENSE. Extended with ID scheme, consistency gate and schemas. -->

# Local scan artifacts and continuity

This adaptation uses ordinary local files, with format marker `mimo-security-scan/v1`. It does not reproduce the Codex database, handoff tokens, artifact seals, native IDs, SARIF export, or token metering. Do not apply the native Codex findings schema to these local outputs.

When consuming an existing `claude-security-scan/v1` report, preserve its original format marker and source identity as input provenance. New output from this MiMo Code adaptation uses `mimo-security-scan/v1`; do not relabel imported evidence as a new scan.

Field-level shapes and prose templates: [report-templates.md](report-templates.md). Machine schemas: [schemas/](schemas/). Deterministic checks: `scripts/validate_artifacts.py`.

## Required artifacts

For a complete scan, write these files to one output directory:

- `scan-manifest.json`: format marker, target label, actual revision or snapshot identity when known, requested scope and exclusions, mode, source limitations, completion status, and performed checks. A HEAD revision alone does not identify a dirty worktree. Use a digest only if actually measured over the assessed input.
- `threatmodel.md`: exact supplied model, or the source-backed generated model with facts, assumptions and hypotheses separated. Preserve supplied text; put extra evidence in a separate clearly labeled section or report.
- `findings.json`: an object with the format marker and a `findings` array of validated, reportable findings. Use an empty array when none are established; an empty array never establishes full coverage. **This file is the source of truth for what is a finding.**
- `coverage.json`: requested inventory, fully reviewed paths, exclusions with reasons, remaining paths, supporting paths, rejected/suppressed candidates with counterevidence, deferred candidates with evidence and exact proof gaps, open questions, and a boolean `complete`. Count only files actually fully reviewed in the requested inventory. Reading search hits or architecture snippets is not full review. Deduplicate overlapping passes.
- `report.md`: scope and source identity, executive findings summary, source-backed findings, validation basis, counterevidence, severity/confidence, actual coverage, remaining work and next actions. Distinguish no findings in reviewed material from a claim that the repository is secure.

## Consistency gate (hard)

Before delivery, enforce:

1. Every `F*` id in `findings.json` appears in `report.md` exactly once as a detailed finding.
2. `report.md` contains no finding id absent from `findings.json`.
3. Disproven or suppressed candidates appear only under Suppressed / Disproven as `CAND-*` (optionally `was_drafted_as: "F2"`). They never occupy a findings table row.
4. No `CAND-*` id appears both as a finding and as a suppressed candidate.
5. `coverage.fully_reviewed_paths` ∩ `coverage.remaining_paths` = ∅.
6. Path strings are repository-relative and free of trailing annotations (" (path builders…)").
7. `complete: true` only when `remaining_paths` is empty and no reportable candidate is still pending.
8. `findings[].reportable` is true or the entry does not belong in `findings[]`.
9. Severity ∈ {critical, high, medium, low}; confidence ∈ {high, medium, low}; never one combined label.

Run:

```bash
python scripts/validate_artifacts.py <output-dir>
```

Exit 0 with warnings is deliverable after review; exit 1 must be fixed. The script does not test factual correctness.

## Finding fields

Every finding retains a stable local ID (`F1`, `F2`, …), title, vulnerability family and CWE when established, attacker, controlled input, prerequisites, violated invariant, source-to-sink path, root cause, impact, mitigation and counterevidence. Include exact repository-relative `locations` with `path`, `startLine`, optional `endLine`, and roles such as `entrypoint`, `root_control`, `sink`, and `concrete_implementation`. Evidence entries contain actual inspected code or observed results and explain what they establish. Separate calibrated severity (`critical`, `high`, `medium`, `low`) from confidence (`high`, `medium`, `low`) and state the reason for each. Do not invent line numbers or runtime output.

Gates (`F*.gates`) record exploitability prerequisites that static audit cannot settle (server policy, live config, another component). A gated finding stays reportable with `status: reportable_with_gate` when the static path is otherwise solid; state how each gate resolves.

## Candidate continuity

When a standalone phase is requested, or between passes, maintain one `candidates.json` collection or the same inline candidate collection if no files were requested. Preserve each candidate ID (`CAND-…`), original source evidence, affected instances and order. Discovery adds plausible candidates; validation adds `reportable`, `suppressed`, `not_applicable`, `disproven`, or `deferred` and its basis; attack-path analysis adds its facts and final decision. Every candidate receives an explicit outcome. Pending candidates never enter the validated findings array.

If detailed artifacts are requested, use `findings/<id>/discovery.md`, `validation.md`, `attack-path.md`, or `fix.md` within the output directory. Store actual PoCs, crafted inputs and logs in `findings/<id>/validation-artifacts/`. Do not create empty directories or placeholder proof. Writeups may use `findings/<slug>/<slug>.md`. Hardening output goes in `hardening/` without changing the evidence collection.

## Resume and drift

Checkpoint a longer audit as ordinary local JSON with `complete: false` and honest partial coverage. Resume only against the same input identity (`scripts/bind_source.py` binding); record source drift rather than silently treating a different checkout as the old target. Complete the report only after every requested path and candidate has a recorded outcome, or explicitly deliver partial results. If token usage is unavailable, say unavailable and do not estimate it.

Validate JSON syntax, citations and result-relative links before delivery. JSON parsing validates syntax, not factual accuracy or full schema conformance. Specialized patch-risk and triage skills keep their own documented contracts.
