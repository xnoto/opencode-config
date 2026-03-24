---
name: opencode-config-maintenance
description: Maintain this OpenCode configuration repo when the task involves opencode.json, agent prompt files, AGENTS.md routing rules, MCP server toggles, permissions, or repo-local runtime behavior. Use for safely extending or refining how this OpenCode environment behaves when deployed from this repository.
---

# OpenCode Config Maintenance

Use this skill when changing how the OpenCode environment behaves.

## Scope

- `opencode.json`
- `AGENTS.md`
- `agent/*.md`
- `prompts/*.md`
- repo-local `skills/`

## Workflow

1. Read the affected config and nearby prompt files first.
2. Preserve existing permission posture unless the user explicitly wants broader access.
3. Keep changes minimal and consistent with current conventions.
4. Call out deployment-facing effects such as changed permissions, enabled MCP servers, or altered default behavior.
5. Verify JSON validity and file paths after editing.

## Guardrails

- Do not silently broaden permissions.
- Do not enable external MCP services unless the user asks.
- Do not remove routing protections from `AGENTS.md` unless explicitly requested.
- Treat agent prompts as shared runtime policy; avoid stylistic churn.

## Validation

- Re-read edited files.
- If `opencode.json` changes, validate that the JSON remains well-formed.
- Summarize any deployment implications plainly.
