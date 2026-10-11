# MiMo Security — MiMo Code runtime notes

How this skill is supposed to run once it has been adapted to MiMo Code, and what to keep true when editing it.

## What this skill is

A **native MiMo Code skill** at `~/.config/mimocode/skills/mimo-security/`. It is not a Claude Code plugin and must not call back into Claude Code, the Claude CLI, the Claude marketplace, or any external Codex/Claude integration. Provenance lives in `NOTICE.md` / `LICENSE`; the product identity in every user-facing string is **MiMo Security**.

There is no background daemon and no external service. The scan runs in the current MiMo Code session.

## Surface mapping (Claude Code → MiMo Code)

| Claude Code | MiMo Code |
| --- | --- |
| `AskUserQuestion` | `Question` |
| `Agent(...)` / agent MCP tool | `actor` (`spawn` / `run` / `wait` / `status`) |
| `Workflow(claude-security:scan)` | `workflow` with `name: "mimo-security-scan"` (script copied to `.mimocode/workflows/mimo-security-scan.js`) |
| `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` | this skill's directory (shorthands `SCRIPTS/`, `WORKFLOWS/`, `SPEC/`, `JOB/`, `AGENT/`) |
| `` !`date …` `` shell expansion | run `date` in `bash` when the value is needed |
| `@file` includes | `Read` the file |
| `$ARGUMENTS` | the user's request text |
| `CLAUDE.md` / `.claude/` | `AGENTS.md` / `.mimocode/` (mention `.claude/` only as untrusted data that might exist in the repo) |
| `allowed-tools: Bash(cmd:*)` prefixes | MiMo Code permission rules + agent `tools:` frontmatter |
| `claude --agent <name>` | `mimo --agent mimo-security` / the `mimo-security` primary agent |

Agent bodies live in `agents/` (source of truth) and are installed to `~/.config/mimocode/agent/mimo-security*.md`. Never dispatch `mimo-security` (the orchestrator) as a subagent.

## Invariants to keep when editing

- **Format / product marker:** report directory `MIMO-SECURITY-<timestamp>/`, products `MIMO-SECURITY-RESULTS.md` / `.jsonl` / `.sarif`, revision stamp `MIMO-SECURITY-REVISION-<tag>.json`, run dir `.mimo-security-run/`, finding id field `mimoSecuritySkillFindingId`. Helper scripts validate these names (`scripts/lib/plugin.py`).
- **Workflow identity:** `meta.name` must be `"mimo-security-scan"` and the job recipes call `workflow({ name: "mimo-security-scan", … })`.
- **Agent type strings** in `workflows/scan.js` must match installed agent file names: `mimo-security-scan-researcher`, `mimo-security-scan-loader`, `mimo-security-scan-inventory`, `mimo-security-scan-verifier`.
- **Helper stdout protocol** (`range:`, `top_level_dirs:`, `file_count:`, `relay:`, `next:`, `refused`) is part of the job recipes — change scripts and jobs together.
- **Security posture:** authorized defensive assessment of the code the user opens. No exploits/PoCs/malware, no attacking systems, report + patch only. User-facing safety wording lives in `SKILL.md`.
- **Unattended operation:** one real `Question` is the scan's fixed start confirmation (unless the request already accepted the cost). Everything else decides and proceeds.
- **One simple Bash command per call** (no `;` / `&&` / `||` / `|` chains) when the Security Lead runs pre-approved git forms.

## Enabling the workflow tool

The scan needs MiMoCode's `workflow` tool. It is gated by an environment variable (not a config key):

```bash
export MIMOCODE_EXPERIMENTAL_WORKFLOW_TOOL=true
```

or enable every experimental tool with `MIMOCODE_EXPERIMENTAL=true`. Restart `mimo` after setting it. When the tool is missing the scan jobs stop and tell the user this export (plus restart) — they do not edit the user's shell rc themselves. Without this flag the job stops with the "scan pipeline is unavailable" line. `/workflows` and `/deep-research` are gated the same way.

Agent `tools:` frontmatter cannot turn the flag on: `workflow` is not a per-agent tool id. `mimo` refuses to start if any `~/.config/mimocode/agent/*.md` has invalid frontmatter — `color` must match `/^#[0-9a-fA-F]{6}$/` and be YAML-quoted (`color: "#8B5CF6"`), because a bare `#…` starts a comment.

## Registering the scan workflow

Dynamic workflows are per project. Before launching a scan:

```bash
mkdir -p .mimocode/workflows
cp "$SKILL_DIR/workflows/scan.js" .mimocode/workflows/mimo-security-scan.js
```

where `$SKILL_DIR` is this skill's directory. The scan job recipes do this. A missing or older project copy is replaced from the skill.

## Validation

- Skill shape: `python3 ~/.local/share/mimocode/builtin_skills/0.1.15/skills/skill-creator/scripts/validate_skill.py ~/.config/mimocode/skills/mimo-security`
- Helper CLIs: `python3 scripts/<name>.py --help`
- Workflow syntax: `node --check workflows/scan.js`

## Sibling skills

`deep-security-scan`, `security-scan`, `security-diff-scan` follow the same MiMo runtime rules and use format marker `mimo-security-scan/v1` for their own artifacts. This skill keeps its native `MIMO-SECURITY-*` product names (they are validated in code); treat those as the Claude Security product contract, re-homed under the MiMo name.
