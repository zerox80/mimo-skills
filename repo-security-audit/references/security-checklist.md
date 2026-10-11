# Security Checklist

Adapt checks to the actual repository architecture. Do not blindly apply irrelevant categories. For every candidate, run the Required Analysis Method below before classifying.

## Required Analysis Method

For each suspicious code path:

1. Identify the attacker-controlled entry point.
2. Trace the input through relevant functions and components.
3. Identify the sensitive operation or security boundary.
4. Inspect all existing validation and protection mechanisms.
5. Determine realistic exploitability.
6. Establish the potential security impact.

**A suspicious function or dangerous-looking pattern alone is not proof of a vulnerability.**

---

## 1. Authentication and Authorization

- Authentication bypass
- Authorization bypass
- Privilege escalation
- IDOR
- BOLA and BFLA
- Cross-user data exposure
- Cross-tenant access violations
- Session fixation
- Session hijacking weaknesses
- JWT validation errors (algorithm confusion, missing `exp`/`aud`/`iss`, signature skip)
- Token verification bypass
- Insecure password-reset mechanisms
- Missing access-control enforcement

## 2. Injection and Code Execution

- SQL injection
- NoSQL injection
- Command injection
- OS command execution
- Server-side template injection
- Remote code execution
- Unsafe deserialization
- Code evaluation of untrusted input
- LDAP and XML injection where applicable
- Path traversal
- Arbitrary file read or write
- Unsafe file uploads

## 3. Web and API Security

- Cross-site scripting (stored, reflected, DOM)
- Cross-site request forgery
- Server-side request forgery
- Open redirects with concrete security impact
- Broken API authorization
- Insecure CORS configurations
- Insecure cookie handling (`HttpOnly`, `Secure`, `SameSite`, scope)
- Missing security controls (CSP, HSTS, frame options, rate limits where security-relevant)
- Unsafe input processing
- Sensitive information exposure (stack traces, verbose errors, debug endpoints)

## 4. Infrastructure and Supply Chain

- Hardcoded credentials
- Exposed API keys
- Secret leakage (source, logs, CI, artifacts)
- Dangerous deployment configurations
- Insecure CI/CD workflows (untrusted checkout execution, secret exposure to forks, injection via PR title/body)
- Dependency vulnerabilities with verifiable affected versions
- Container security misconfigurations (privileged, root, exposed docker.sock, secrets in image)
- Excessive permissions (IAM, K8s RBAC, cloud roles)
- Insecure service-to-service communication
- Unsafe trust boundaries

## 5. Advanced Security Issues

- Business logic vulnerabilities
- Race conditions
- TOCTOU vulnerabilities
- Cryptographic misuse (weak algorithms, static IVs/nonce reuse, custom crypto, missing signature verification)
- Webhook authentication bypass
- Insecure multi-tenant isolation
- Security-relevant denial-of-service vulnerabilities (resource exhaustion reachable from untrusted input, unbounded queries)
- Privileged operations reachable from untrusted contexts

---

## Severity Classification

### P0 — Critical

Only when actual security impact and attack prerequisites justify it:

- Broadly reachable unauthenticated remote code execution
- Systemic authentication bypass
- Catastrophic cross-tenant compromise
- Critical infrastructure takeover
- Widespread privileged access without authentication

### P1 — High

- Exploitable privilege escalation
- Significant authentication or authorization bypass
- Serious sensitive-data exposure
- Exploitable injection with substantial impact
- High-impact authenticated code execution
- Serious cross-tenant isolation failures

### P2 — Medium

- Practically exploitable security weaknesses with limited impact
- Authorization flaws with restricted scope
- Security-sensitive information disclosure
- Exploitable weaknesses requiring significant prerequisites
- Moderate-impact web or API vulnerabilities

### Severity factors

Account for:

- Actual reachability
- Required authentication
- Required attacker privileges
- Attack complexity
- Existing defenses
- Exploitation prerequisites
- Confidentiality impact
- Integrity impact
- Availability impact
- Affected users and systems

Do not artificially inflate severity. Do not include P3/P4 findings in the primary vulnerability report.
