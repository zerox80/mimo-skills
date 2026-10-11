# Validation Protocol

Every candidate vulnerability must undergo rigorous validation.

**Maximum: THREE validation passes per finding. Never exceed this limit.**

This limit is shared across parent and child agents. A subagent does not reset the validation counter.

---

## Pass 1: Technical Verification

Inspect the original code evidence.

Verify:

- Exact vulnerable code location
- File path and line numbers
- Attacker-controlled input
- Relevant execution path
- Reachability
- Existing mitigations
- Sensitive operation
- Realistic security consequence

Reject candidates that cannot satisfy the essential vulnerability requirements.

**Output:** evidence table (file:line → claim), reachability verdict, preliminary severity, state.

## Pass 2: Independent Reverification

Reevaluate the vulnerability independently. Do not simply repeat the original reasoning. Actively try to disprove the vulnerability.

Check:

- Whether another function blocks exploitation
- Whether middleware prevents the attack
- Whether authentication or authorization is enforced elsewhere
- Whether input sanitization is effective
- Whether the vulnerable code is actually reachable
- Whether framework behavior invalidates the hypothesis
- Whether configuration prevents exploitation
- Whether attacker prerequisites are realistic

Use safe and non-destructive local verification when available.

Reject false positives immediately.

**Output:** contradicting evidence found or not, remaining uncertainty, state change.

## Pass 3: Final Adversarial Verification

Only execute this pass when uncertainty remains.

Perform a final critical review of:

- Attack feasibility
- Execution path
- Exploitation assumptions
- Missing safeguards
- Existing protections
- Attack prerequisites
- Impact assessment
- Severity classification

Attempt to find evidence contradicting the vulnerability. Make the final determination.

**Output:** final state, severity confirmation or demotion, residual uncertainty.

---

## Validation Rules

- Never perform more than three validation passes.
- Stop early when sufficient evidence is available.
- Never assume that three passes automatically establish validity.
- Never invent successful exploitation or verification results.
- Never report a vulnerability as confirmed without sufficient evidence.
- Deduplicate findings with the same root cause.
- Clearly document validation limitations.
- Parent + subagent passes count together toward the limit of three.

---

## Final Validation States

### CONFIRMED

Sufficient code evidence or safe reproduction establishes the vulnerability, including its realistic reachability and security impact.

- Must appear in the primary report (section 3).
- Counts toward confirmed P0/P1/P2 totals.

### LIKELY

Strong evidence exists, but a material uncertainty remains unresolved.

- Report separately (section 4). Do not count as confirmed.
- State which evidence would resolve the uncertainty.

### UNCONFIRMED

The evidence is insufficient to establish a genuine vulnerability.

- Report separately (section 4). Do not count as confirmed.

### REJECTED

Analysis disproves the vulnerability hypothesis.

- Document briefly in section 5 with rejection reason.
- Do not include in vulnerability counts.

Only count CONFIRMED findings as confirmed vulnerabilities. Report LIKELY and UNCONFIRMED candidates separately. Do not present uncertain issues as established vulnerabilities.

---

## Deduplication

- Same root cause → one finding, even if multiple sinks or call sites.
- Keep the strongest evidence chain and the highest realistic severity.
- List secondary locations under the primary finding.

## Safe Verification Constraints

Permitted:

- Static analysis and source reading
- Isolated, authorized, non-destructive local checks
- Reading tests and fixtures for intended behavior

Forbidden:

- Modifying application code or config
- Executing destructive or production-facing exploits
- DoS / resource-exhaustion testing
- Installing dependencies without explicit permission
- Running untrusted project scripts without approval
- Exfiltrating or broadcasting secrets

If safe dynamic verification is impossible, use static evidence and document the limitation under Residual Uncertainty.
