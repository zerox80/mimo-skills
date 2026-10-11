# Pass playbooks

Concrete work for each deep-security-scan pass. A pass that only rereads the previous report is not another audit. Every pass must open source files and record newly inspected paths.

Read [finding-families.md](finding-families.md) for sink catalogs while executing a playbook.

## Universal pass contract

Every pass returns:

1. **Candidates** — stable ID, title, source evidence with `path:line`, affected instances, strongest counterevidence, proof gaps.
2. **Covered paths** — clean repository-relative file paths that were *fully* reviewed in this pass (not search hits).
3. **Supporting paths** — files consulted for context but not fully reviewed.
4. **Exclusions** — skipped paths and the reason.
5. **Unresolved gaps** — exact questions that block a stronger conclusion.
6. **New work claim** — at least one concrete thing this pass did that the prior pass did not do (new files, new sink variant, new attacker perspective).

Search hits, architecture snippets and prior-report restatements are never "covered paths".

---

## Pass 1 — Baseline (forward + architecture)

**Goal:** map the product and produce the first source-backed candidate set.

### Required work

1. **Architecture map** (follow [threat-model.md](threat-model.md)):
   - product purpose, users, supported surfaces (web, API, CLI, library, mobile, job, plugin);
   - entry points and trust boundaries with `path:line` anchors;
   - protected assets and security invariants;
   - configuration / deployment prerequisites that change a boundary.
2. **Entrypoint inventory.** Enumerate every attacker-reachable surface actually present:
   - HTTP routes / RPC handlers / message consumers;
   - CLI commands and flags;
   - exported mobile components, deep links, content providers;
   - library public APIs and plugin hooks;
   - file parsers, import/export, upload handlers;
   - scheduled jobs and webhooks.
3. **Forward traces.** For each major entrypoint class, follow attacker-controlled data toward sensitive operations. Use [finding-families.md](finding-families.md).
4. **Credential sweep** (see [core-scan.md](core-scan.md) "Secrets Exposed in Source").
5. **SECURITY.md policy chain** via [security-guidance.md](security-guidance.md).
6. Produce candidates with evidence *and* counterevidence. Do not stop at "this looks dangerous".

### Minimum new work

- Fully review every high-value entrypoint file in scope (manifests, routers, main CLIs, public API modules).
- At least one forward trace per major surface found.

### Forbidden

- Treating threat-model hypotheses as findings.
- Claiming coverage of a file you only grepped.

---

## Pass 2 — Challenge (backward + authorization + siblings)

**Goal:** break pass-1 assumptions and find what baseline missed.

### Required work

1. **Backward traces.** Start at sensitive sinks (exec, eval, SQL, filesystem write, deserialization, SSRF, secret use, authz decisions) and walk callers to a plausible attacker. Prefer sinks baseline did not open.
2. **Authorization and business logic:**
   - ownership / tenant / role checks and their absence on sibling operations;
   - IDOR patterns: object ID from request used without ownership check;
   - state-machine skips (e.g. approve without create, delete without ownership);
   - multi-step workflows where one step is guarded and another is not.
3. **Sibling entrypoints.** For every interesting sink found in pass 1, find *other* callers and config-selected variants (platform, feature flag, deployment, legacy path).
4. **Challenge every pass-1 candidate.** Re-read the cited lines. Try to disprove it. Record concrete counterevidence. If disproven, outcome is `disproven` — it must not reappear as a finding.
5. **Concrete sink variants.** Same family, different API (e.g. not just `exec` but `execFile`, `spawn` with shell, template render, `yaml.load`).

### Minimum new work

- At least one full backward trace per major sensitive-operation class.
- Explicit disposition (keep / revise / disprove) for every pass-1 candidate.
- Sibling-entrypoint list for the top sinks.

### Forbidden

- Rewording pass-1 findings without opening new source.
- Dropping a candidate silently — every candidate gets an outcome.

---

## Pass 3 — Proof gaps (open-ended + static proof)

**Goal:** close what is still unproven and validate the survivors.

### Required work

1. **Gap hunt.** List remaining proof gaps from passes 1–2. For each, inspect the smallest source set that could close it (config, tests, docs, generated code, deployment files).
2. **Strongest benign explanation.** For each surviving candidate, write the best innocent story and test it statically. Reject only with concrete counterevidence.
3. **Validation of unique survivors.** Apply [static-finding-assessment.md](static-finding-assessment.md). A complete static proof can support a finding without runtime reproduction; label the basis.
4. **Coverage reconcile.** Deduplicate covered paths across passes. Compare to the bound inventory. Finish remaining high-value files or mark them remaining.
5. **Severity/confidence calibration** with the matrix in [core-scan.md](core-scan.md). Keep gates explicit when exploitability depends on untested external behavior.

### Minimum new work

- Concrete disposition of every open proof gap (closed / deferred with `how_to_resolve`).
- At least one benign-explanation test with source citations.
- Coverage table that adds up (reviewed + remaining + exclusions ≈ inventory).

### Forbidden

- Inventing runtime results to fill gaps.
- Marking `complete: true` while remaining paths or unresolved reportable candidates exist.

---

## Pass N+ (4+) — Rotating angles

Pick an unused angle and do substantive new source inspection:

| Angle | Focus |
|---|---|
| Supply chain | dependency pins, build scripts, CI workflows, release paths, update mechanisms |
| Crypto & secrets | key lifecycle, randomness, TLS/pinning, secret storage and disclosure paths |
| Parser / deserialization | every untrusted parse surface, size limits, type confusion, gadget reachability |
| Concurrency / TOCTOU | check-then-act, race on shared state, session fixation windows |
| Multi-tenant isolation | cross-tenant IDOR, cache key confusion, shared resource leakage |
| Error & logging | secret leakage in errors/logs, stack traces to untrusted clients |
| Deployment reality | config precedence, mount/path resolution, default credentials, debug flags in prod paths |

State which angle and what new paths it covered.

---

## Product-surface quick maps

Use the map that matches the bound target; mix when the product is hybrid.

### Web / HTTP service

- routing table → middleware (authn/authz, CSRF, CORS, body limits) → handler → data layer
- session lifecycle, cookie flags, redirect targets, SSRF via user URLs
- template/render sinks, JSONP, file upload/download paths
- admin/debug endpoints, health/metrics exposure

### CLI / daemon

- argument parsing → config precedence (flags > env > files > defaults)
- file and path handling, `--` end-of-options, shell metacharacters
- privilege drops, temp file creation, signal handling
- plugin/extension loading

### Library / SDK

- public API surface and safe defaults
- caller obligations documented vs enforced
- parser entrypoints, serialize/deserialize
- credential and network sinks in helpers

### Mobile (Android/iOS)

- exported components, deep links, intent/URL schemes
- WebView bridges, JS interfaces, cookie/Bearer attachment
- FileProvider / content URI exposure, path joins from remote names
- IPC (exported services, broadcast receivers), backup rules, keystore usage

### Infrastructure / IaC / CI

- cloud resource exposure (public buckets, open security groups)
- secrets in workflows, pull_request_target, script injection in Actions
- container base images, entrypoints, mounted credentials

### Desktop / Electron

- `nodeIntegration`, `contextIsolation`, preload bridge surface
- custom protocol handlers, auto-updater signature checks
- IPC handlers exposed to renderer
