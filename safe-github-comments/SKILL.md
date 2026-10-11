---
name: safe-github-comments
description: Hard approval gate for every GitHub comment, review, or review-comment write. Drafts the exact text and target first, shows it to the user, and posts only after explicit OK. Use whenever about to post a PR comment, PR review, inline review comment, issue comment, or review submission via gh or the GitHub API — triggers include "comment on PR", "leave a review", "post feedback", "review this PR and leave comments", "schreib einen Kommentar", "Kommentar auf den PR", "Review abgeben", "Feedback hinterlassen". Never post proactively without a clear user request. Do NOT use for read-only PR/issue work, creating PRs, or pushing code that leaves no comments.
---

# Safe GitHub Comments

## Important

**NEVER** post any GitHub comment, review, review comment, issue comment, or review submission without explicit user approval. This is non-negotiable.

- No proactive comments — even if the user asked for a review earlier in the session, still show the draft and wait.
- "100% sure" means the user has seen the exact planned text and said OK (or "post it", "ja", "senden", etc.). Silence, a thumbs-up emoji alone, or a related instruction is NOT approval.
- If unsure whether the user wants a comment posted: ask first, then draft.

This gate applies to every write that leaves text visible to others on GitHub:
- PR review comments (inline, file:line)
- PR review bodies (`gh pr review`, submit as comment/approve/request-changes)
- Issue and PR conversation comments (`gh issue comment`, `gh pr comment`)
- Any `gh api` call that creates reviews or comments (`/reviews`, `/comments`, `/issues/comments`)

It does **not** apply to: reading PRs/issues/diffs, creating PRs, pushing commits, editing the PR title/body of your own PR, or local git operations.

## Instructions

### Step 1: Confirm intent

Before drafting, confirm the user wants a GitHub comment posted at all.

- User explicitly asked ("comment on PR #123", "leave a review") → continue.
- You only *want* to comment (e.g. after fixing something) → stop and ask: "Soll ich dazu einen PR-Kommentar posten?" Do not draft until they say yes.

### Step 2: Draft the complete payload

Write the full planned write as a draft. Never post a partial or placeholder text.

Show all of:

| Field | Value |
|-------|-------|
| Action | `inline review comment` \| `review body` \| `issue/PR comment` \| `review submit (COMMENT/APPROVE/REQUEST_CHANGES)` |
| Target | `owner/repo#123` (+ `file:line` for inline) |
| Text | the exact body, in a fenced block |

For multi-part reviews (body + several inline comments), list **every** piece in order. Nothing may be omitted from the preview.

### Step 3: Hard gate — wait for explicit OK

Stop and ask clearly:

```
Soll ich das so posten? [ja / nein / Änderungen]
```

Wait. Do not call any write tool in the same turn as showing the draft.

### Step 4: Post only after OK

If (and only if) the user explicitly approved:

1. Post with the exact text shown (re-check you are not "improving" it silently).
2. Report back with the resulting URL(s).
3. If the user requested changes to the draft: revise, show the new draft again, return to Step 3.

If the user said no / "noch nicht" / edited without approving: do nothing.

### Step 5: Multi-write sessions

Each new comment or review is a new draft + new approval. Approving one write does not authorize the next.

## Examples

**User:** "Comment on PR #42 that the tests need more coverage for the timeout path."
**Actions:** Draft the comment text + target `owner/repo#42` → show it → wait → post after "ja" → return URL.

**User:** "Review PR #17 and leave feedback."
**Actions:** Read the PR → draft review body and any inline comments → show the full plan → wait → post only after OK.

**Agent finished a fix and wants to say so on the PR.**
**Actions:** Ask first ("Soll ich das als PR-Kommentar festhalten?"). Do not post.

**User:** "Post it." (after you showed a draft)
**Actions:** Post exactly that draft. Do not start a new one.

**User:** "Mach mal einen Kommentar auf den PR."
**Actions:** Draft in German if the PR/user language is German → show → wait → post.

## Troubleshooting

| Situation | Cause | Fix |
|-----------|-------|-----|
| Posted without showing text | Skipped Step 2/3 | Never skip. If already posted, apologize and do not delete without asking. |
| User said "ok" to the idea but not the text | Ambiguous approval | Re-show the draft and ask for explicit OK on the text. |
| Long multi-part review | Easy to forget an inline comment | Number every piece in the preview; post them all only after OK on the full list. |
| Unclear if a write is "a comment" | e.g. review submit, issue comment | Treat any user-visible GitHub text write as gated. When unsure, gate. |
| User language is German | — | Draft and ask in German; keep code/identifiers as-is. |
