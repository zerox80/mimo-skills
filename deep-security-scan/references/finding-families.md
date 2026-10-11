# Finding families and sink catalogs

Use these as a checklist and as source for concrete search patterns. A keyword match is never a finding — establish the actual source → control → sink path. Adapt names to the bound stack; missing language support is not a missing vulnerability class.

Severity and confidence rules live in [core-scan.md](core-scan.md). Assessment shape lives in [static-finding-assessment.md](static-finding-assessment.md).

---

## Injection

| Family | Attacker input | Weak controls | Sinks (examples) | Common false positives |
|---|---|---|---|---|
| SQL / NoSQL | query params, filters, sort fields, JSON bodies | string concat, format strings, insufficient ORM misuse | `execute`, `raw`, `query`, `aggregate`, `whereRaw`, `find_by_sql`, `$where` | parameterized queries, allowlisted sort columns |
| Command | filenames, URLs, branch names, user names | partial escapes, `shell=True`, template-built commands | `os.system`, `subprocess` w/ shell, `exec`, `child_process`, `Runtime.exec`, backticks | fixed argv arrays, allowlisted commands |
| Code / template | templates, expressions, config | `eval`, dynamic import, SSTI | `eval`, `exec`, `pickle.loads`, `yaml.load`, `vm.run`, ERB/Jinja with user data | sandboxed expression languages |
| LDAP / XPath / header | headers, XML, filters | string-built filters | LDAP filters, XPath, CRLF in `Set-Cookie`/`Location` | encoded/validated headers |
| Path | filenames, archive members, `..` segments | join without containment check | `File(parent, name)`, `open`, `path.join`, `os.path.join`, `ZipFile.extract` | id-based paths, realpath containment |

**Prove:** data flows from a source the attacker controls into the sink without a control that neutralizes the dangerous interpretation. Quote the join/format line.

---

## Web / client-side

| Family | Look for | Sinks | Prove |
|---|---|---|---|
| XSS (reflected/stored/DOM) | untrusted data in HTML/JS/attr/URL | `innerHTML`, `document.write`, `dangerouslySetInnerHTML`, `| safe`, `v-html`, `render` w/ raw HTML | no encode/escape on the exact path; browser context (HTML vs JS vs URL) |
| CSRF | state-changing cookie-auth endpoints | missing anti-CSRF token / SameSite | cross-site request can carry session and mutate state |
| Open redirect | user-controlled redirect target | `Location`, `window.location`, `router.push` | no allowlist; attacker chooses destination after auth or on login |
| SSRF | user URL fetched server-side | `fetch`, `requests`, `axios`, `urllib`, `http.get`, cloud metadata clients | no host allowlist / block of link-local and metadata IPs; response returned or used |
| Clickjacking / frame | missing `X-Frame-Options`/`frame-ancestors` | response headers | state-changing or sensitive UI framed cross-origin |

---

## Authorization and multi-tenant

| Family | Pattern | Prove |
|---|---|---|
| Missing authn | route/handler without session/principal check | reachable without credentials on a non-public surface |
| Missing authz / IDOR | object id from request → fetch/write without ownership check | attacker with account A can reach object of B; cite both the id source and the load |
| Tenant isolation | cache keys, query filters, storage prefixes missing tenant | cross-tenant read/write path |
| Privilege escalation | role change, admin flag from client, mass assignment | client-controlled field changes authority |
| Business logic | step skip, negative quantities, race on limit, coupon reuse | concrete state machine abuse with impact |
| CORS misconfig | `Access-Control-Allow-Origin: *` with credentials or reflected origin | browser can read authenticated responses from attacker origin |

---

## Sensitive data and secrets

| Family | Pattern | Prove |
|---|---|---|
| Hardcoded credentials | API keys, passwords, private keys, tokens in source | format + purpose; distinguish public client IDs, placeholders, env refs |
| Secret disclosure | secrets in logs, errors, URLs, client bundles, APKs | secret reaches a reader who should not have it |
| Insecure storage | plaintext tokens, world-readable files, weak keystore | attacker-reachable read path |
| Weak crypto | ECB, fixed IV, MD5/SHA1 for security, `Math.random` for tokens, custom crypto | security-relevant use, not checksums |
| Transport | cleartext HTTP, missing cert validation, optional TLS | credential or auth data on the wire |

Follow the disclosure-path rules in [core-scan.md](core-scan.md). Never use discovered credentials.

---

## Deserialization and parsing

| Family | Sinks | Prove |
|---|---|---|
| Insecure deserialization | `pickle`, `yaml.load`, `ObjectInputStream`, `Marshal`, `unserialize`, JSON revivers | attacker controls bytes; gadget or type-confusion reachability |
| XXE | XML parsers with external entities enabled | untrusted XML + entity expansion / file disclosure |
| Archive / path | `ZipFile`, `tar`, `untar`, `Expand-Archive` | member name escapes destination root |
| ReDoS / parser DoS | untrusted regex, deep JSON, huge headers | only if impact is realistic on the actual service |

---

## Filesystem and process

| Family | Pattern | Prove |
|---|---|---|
| Path traversal | remote/local name joined into a path | escapes intended root; cite path math |
| Arbitrary file write/read | upload/download helpers without containment | attacker chooses path or content at a sensitive location |
| Unsafe temp | predictable temp names, `/tmp` races | attacker can pre-create or swap |
| Command execution via files | include/exec of user-uploaded or user-controlled path | file content or name reaches execution |
| Symlink following | extract/copy without `O_NOFOLLOW` / realpath check | attacker-planted link crossed a trust boundary |

---

## Network and request handling

| Family | Pattern | Prove |
|---|---|---|
| Request smuggling | reverse-proxy vs backend length disagreement | only with concrete proxy/backend pair evidence |
| Header injection | CRLF in header values from user input | response splitting / cache poisoning |
| WebSocket / SSE | missing origin checks, auth on upgrade | untrusted origin gets authenticated stream |
| Redirect following + auth | HTTP client re-sends Authorization on redirect | attacker-influenced Location receives the credential |

---

## Supply chain and build

| Family | Pattern | Prove |
|---|---|---|
| Dependency confusion | publish names not reserved internally | install path can fetch attacker package |
| CI script injection | untrusted input in workflow commands (`github.event.*`) | attacker-controlled PR title/branch reaches a shell |
| Release/update integrity | unsigned updates, HTTP download of executable | attacker can serve a malicious artifact |
| Build secrets in artifacts | keys in docker layers, APKs, public assets | secret shipped to clients |

---

## Platform-specific extras

### Android

Exported `activity`/`service`/`receiver`/`provider`; deep links and custom schemes; WebView `addJavascriptInterface` and `setJavaScriptEnabled`; `FileProvider` roots; `pendingIntent` mutability; backup rules; keystore vs SharedPreferences; path joins from remote names.

### iOS

Universal links / custom URL schemes; `UIWebView`/`WKWebView` message handlers; keychain accessibility; App Transport Security exceptions; pasteboard exposure; insecure `NSFileCoordinator` paths.

### Electron / desktop

`nodeIntegration: true`, disabled `contextIsolation`, preload `contextBridge` surface, `shell.openExternal` with untrusted URL, auto-updater signature, custom protocol handlers.

### Python web

`pickle`/`yaml.load`, `render_template_string`, `mark_safe`, `subprocess` with `shell=True`, `open(user_path)`, Flask/Django debug, `SECRET_KEY` defaults.

### Node web

`eval`/`Function`, template literals into SQL/command, `child_process` with shell, `path.join` without containment, `vm`, prototype pollution via `merge`/`extend`, express middleware auth order.

### Go

`exec.Command` with user args joined, `filepath.Join` without `Rel` check, SQL via `fmt.Sprintf`, `html/template` vs `text/template`, unsafe `yaml.Unmarshal` into `interface{}`.

### JVM

SpEL/OGNL/MVEL injection, `ObjectInputStream`, `Runtime.exec`, path traversal via `new File(parent, name)`, XXE on default SAX/DOM, Log4Shell-class lookups in logs.

### IaC / cloud

Public S3/GCS, `0.0.0.0/0` security groups, IAM `*` actions, secrets in user-data, unauthenticated metadata access, Terraform `local-exec` with interpolated vars.

---

## Severity calibration reminders

- Reserve `critical` for clear, immediately actionable severe compromise.
- Realistic high-impact high-likelihood path → `high`. High impact, medium/unknown likelihood → `medium`.
- Downgrade internal, same-tenant, localhost, constrained paths.
- Self-only or privileged-only behavior without a boundary crossing is not a finding.
- Missing deployment evidence lowers *confidence*, not by itself the vulnerability.
- Gates (untested external prerequisite) stay explicit; do not invent their result.
