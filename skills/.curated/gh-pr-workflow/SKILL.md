---
name: gh-pr-workflow
description: Use when a user asks to inspect, review, summarize, comment on, create, update, or debug GitHub pull requests in this OpenCode environment. Combine local git context with GitHub or gh workflows, keep summaries concise, and follow the repo's explicit approval rules for commits and PR creation.
---

# GitHub PR Workflow

Handle pull request work with a bias toward inspection first and mutation second.

## Typical tasks

- Review a PR and report findings
- Summarize branch changes for a PR body
- Inspect CI or checks status
- Add PR comments or replies
- Create or update a PR after the user asks

## Workflow

1. Gather current branch and diff context.
2. Inspect the PR or branch state through GitHub tools or `gh`.
3. Summarize changes and risks before mutating anything.
4. Create comments, reviews, commits, or PRs only when explicitly requested.
5. Return links or identifiers for anything created.

## Guardrails

- Do not commit unless the user asks.
- Do not push unless the user asks.
- Do not force-push or amend unless explicitly requested and safe.
- Prefer review findings ordered by severity with file references.

## Validation

- If code changes are made, run targeted checks when feasible.
- If only PR metadata or comments are changed, confirm the remote action succeeded.
