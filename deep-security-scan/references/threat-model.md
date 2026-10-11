<!-- Modified for MiMo Code on 2026-10-07. Derived from openai/codex-security at eb73cc0fa64f25f432bace6f8ff3f475038bfc71. Local workflows replace Codex host integration. See NOTICE and LICENSE. -->

# Threat Modeling

Build a source-backed model of how the authorized software is actually used. Keep source review read-only and offline unless the user authorizes other context. Apply the supplied threat model, authoritative knowledge base, and inherited security policy without inventing new authority or exposure. Knowledge-base facts override generated assumptions and repository policies, never explicit user instructions. Threat scenarios guide review; they are not confirmed findings. Generated analysis must not reproduce credential material. For secret-bearing configuration, record the key or secret reference, storage location, recipients, and enforcing control instead of the literal value.

## Establish The Architecture

1. Start at the repository root and identify the product, its users, supported interfaces, and normal execution modes. Include separately authorized import, remediation, administrative, export, and publication workflows as conditional surfaces when supported. Distinguish production code and privileged build or release paths from tests, examples, prototypes, and developer-only tools. Stay within the caller's authorized scope; a standalone model is repository-wide unless the user asks for narrower scope.
2. Follow representative inputs through real entry points, components, controls, and sensitive operations. Identify the actors on each side, the data or authority transferred, protected assets, and the invariant each boundary must preserve. Include authentication, authorization, ownership, tenant isolation, public APIs, parsing and deserialization, storage, network requests, process or code execution, native bindings, credential issuance, and capability grants when relevant. For web services, consider session lifecycle, browser-origin controls, rendering, injection, and request destinations; for cryptographic or privacy-sensitive systems, consider key management, access controls, sensitive-data handling, privacy guarantees, and auditability. Identify safe defaults and caller obligations for libraries, plus resource or spending limits protecting an actual shared service or CI workflow. Use actual imports and callers; do not build a complete call graph or treat keyword matches as proof.
3. For extensions, subprocesses, workers, and tool APIs, distinguish the operations available to each caller from coordinator, host-only, or operator authority. Trace inherited permissions, brokered writes, ownership claims, and the component that actually enforces a restriction. Distinguish advertised tool visibility from enforced caller authorization. For separately authorized mutations or publication, trace preview, approval, application, and readback; identify how the account, target, revision, audience, and exact payload or digest stay bound. Keep independently enforced interfaces distinct instead of collapsing them into a generic prompt-injection story. Inspect generated, minified, or compressed implementation as data when it owns the control; cite its bundle or loader and stable symbols when original source lines are unavailable. Record a specific review gap only when the implementation cannot be inspected. Do not invent isolation between actors that already share the same authority.
4. Work backward from each sensitive consumer through every materially different supported startup or deployment path. Trace the actual file, network, or process operation through helper return values, path joins, configuration precedence, and deployment or mount mappings. Record the concrete non-secret effective value or location, readers/writers or recipients, enforcing control, and source evidence. Resolve derived child paths as well as their configured roots; do not infer a consumer's location from a variable name, intended directory purpose, or mount label. Follow credentials and sensitive state through mounts to host locations, logs, reports, and exports without copying their contents. Compare documented guarantees with those effective values and controls; separate settings or mount declarations do not establish isolation. Record disagreements and distinguish component-owned controls from assumptions about callers, hosts, or external services. Include supported platform differences, such as Windows paths, executable selection, and access controls, when they change a boundary.
5. Cite inspected repository-relative `path:line` locations for architecture facts, entry points, controls, and discrepancies established from code. A citation must support the claim, not merely name an existing file. Retain authoritative knowledge-base and user-context facts as concise, non-verbatim statements labeled by their origin; do not invent repository evidence or expose private document text or locations. Before returning a generated model, batch-check every repository citation against the inventory and verify its line or line range. Resolve paths from the repository root rather than guessing prefixes from the current directory; correct or remove unverified repository references. Separate code-established facts, provided deployment context, conditional assumptions, and unresolved questions. Stop expanding the architecture once the important boundaries and their evidence are clear.

## Architecture cross-check

Perform a separate architecture pass before finalizing the threat map. Reopen the actual sensitive consumers, deployment paths, configuration chains and controls. Use a fresh reviewer only when delegation is available and authorized; otherwise do the same pass sequentially and disclose that it was not independent. Mapping architecture does not count as a completed vulnerability audit.

Verify a compact effective-resource table: consumer, deployment, configuration chain, safe effective value or location, recipients, enforcing control, evidence, and any documentation discrepancy or missing prerequisite. Never record credential values. Preserve a supplied authoritative model unchanged and add any supplemental facts as clearly labeled evidence.

## Derive Threat Scenarios

For each important boundary, establish:

- The realistic attacker, what input or state they initially control, and which privileges they do not already have.
- The entry point, relevant data flow, expected control, sensitive operation, and specific new capability a failure would grant.
- The violated invariant, affected asset, concrete impact, and any configuration, workflow, dependency, or deployment prerequisites.
- Existing effective controls and counterevidence, a practical mitigation, source citations, and remaining uncertainty.

Prioritize scenarios by plausible impact and reachability. Do not assume that an attacker already controls the operator account, trusted configuration, private state, or privileged release infrastructure. A caller-controlled library or parser input can be a real boundary without proof of an observed production deployment. Conversely, a deployment-specific claim must state the exposure it needs. Do not invent remote access, tenants, missing controls, accepted risks, or owner approval.

Keep hypotheses separate from validated vulnerabilities. Independent source-backed validation can establish a finding without runtime reproduction. Record a material unknown as a question instead of claiming either that a control works or that it is broken. Calibrate severity using the applicable policy, actual privilege gain, impact, likelihood, and effective mitigations. Ordinary authorized behavior, self-only effects, and control an attacker already possesses are not new security impact.

## Use within a local scan

Map architecture within the caller's existing scope. Preserve supplied model text unchanged; do not silently replace or widen it. Record its actual declared scope. Keep generated facts and investigation questions attached to the scan as a local partial checkpoint, then retain them in the final result rather than replacing them with an uncited synopsis.

Use these six dimensions when generating a model:

- `summary`: purpose, components, data flow, normal deployment.
- `assets`: protected data, identity, authority, integrity guarantees.
- `trustBoundaries`: actors, transferred data or authority, controls and exact source anchors.
- `attackerCapabilities`: realistic starting capabilities and meaningful new authority a failure could grant.
- `securityObjectives`: enforceable security invariants.
- `assumptions`: prerequisites, exclusions, documentation discrepancies and unknowns.

Reconcile material scenarios with validated findings, source-backed rejection/control evidence or explicit open questions in [scan-artifacts.md](scan-artifacts.md). A hypothesis is never a finding merely because it is in the threat model.

## Standalone Markdown Model

When the caller requests a full generated threat-model document, use these four sections. Do not restate this guide.

1. **Overview:** Explain intended use, supported deployments, primary components, and important data flows. Include a compact component/source table. Where configuration changes a security boundary, include an effective-resource table with columns `Deployment or workflow`, `Resource or capability`, `Configuration and precedence`, `Safe effective value or location`, `Readers, writers, or recipients`, `Enforcing control`, and `Evidence or unknowns`. Use separate rows when startup paths give the same resource different values or authority. Add a small Mermaid diagram when it makes trust zones or component relationships clearer.
2. **Threat Model, Trust Boundaries, and Assumptions:** Identify protected assets and objectives, actors and their starting/non-capabilities, boundary crossings, security invariants, established controls, deployment prerequisites, exclusions, and unknowns.
3. **Attack Surface, Mitigations, and Attacker Stories:** Give a prioritized table with columns `Priority`, `Scenario and capability gain`, `Prerequisites`, `Impact`, `Existing controls`, `Mitigation`, and `Evidence`. Account for each material architecture boundary, including conditional privileged workflows; keep distinct controls separate or explain why no new capability exists. Use concrete repository-specific scenarios and verified source citations. Clearly label scenarios as hypotheses unless independently validated; do not present them as findings or force a fixed count.
4. **Severity Calibration (Critical, High, Medium, Low):** Give concrete examples and counterexamples at each level. Explain which prerequisites or effective controls change severity, and which stories are unsupported or outside the actual security boundary. Keep confidence and missing evidence distinct from impact.

Keep the document reusable across unrelated diffs. Do not center it on changed files or one suspicious subsystem unless the user explicitly requests that scope.
