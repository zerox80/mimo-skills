<!-- Modified for MiMo Code on 2026-10-07. Derived from openai/codex-security at eb73cc0fa64f25f432bace6f8ff3f475038bfc71. Local workflows replace Codex host integration. See NOTICE and LICENSE. -->

# Local artifact storage

Honor the output path selected by the user. Otherwise choose a fresh writable results directory outside the audited source tree and state its location. Resolve it in the current MiMo Code session; do not assume a Claude cloud container or use MiMo's internal memory/database as a scan artifact store.

Use normal authorized file tools. Keep source, inputs, previous reports and existing user files unchanged. A chat-only request can return its requested result inline. Read-only skills such as verify-fix do not write files. If the active mode prevents artifact writes, return supported results inline and report which files were not saved.

Create only actual outputs. Retain real evidence, crafted inputs, logs and PoCs with their source identity. Never fill missing evidence with placeholders or report an unexecuted command as successful. Check result-relative links before delivery.

Follow [scan-artifacts.md](scan-artifacts.md) for local scan output and candidate continuity. These files describe the MiMo Code adaptation; they do not carry a native Codex artifact seal.
