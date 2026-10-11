# Security policy

This skill is a security tool, so it is held to the standard it applies to other people's code. If you find a vulnerability in the plugin itself, report it.

## Reporting a vulnerability

Report security issues **privately** to the maintainer of this MiMo Code skill. Do not open a public issue for a vulnerability in the skill itself.

Do **not** open a public GitHub issue for a security report. Include what you can of: the skill version and the `mimo-security-<timestamp>/` run directory, your platform and MiMoCode version, reproduction steps, and the impact you believe it has.

In scope: a vulnerability in the skill's own code — its scripts, workflow, skills, agent definitions, and hooks.

Out of scope: findings the scan produces about *your* code (best-effort by design, so a missed vulnerability there is a quality issue, not a skill vulnerability); the behavior of the underlying models themselves, such as jailbreaks or harmful content (the channel above routes those too); and anything downstream of a hostile repository, per the trust model below.

## Trust model

**The code you scan is trusted.** A scan and a fix run in your MiMoCode session, under your permissions, with no isolation layer of the skill's own — so the repository's `.git/config`, its `.claude/` / `.mimocode/` settings and hooks, and everything else your session loads from that directory apply as usual. The skill does not attempt to stop a hostile repository from influencing a scan.

To work with code you do not fully trust, sandbox the whole session first. We suggest [sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime), which enforces filesystem and network restrictions at the OS level without a container; its own README covers how to run MiMoCode inside it.

## Supported versions

Security fixes land on the latest version of the skill. There are no long-lived support branches. Update to the newest version before reporting.
