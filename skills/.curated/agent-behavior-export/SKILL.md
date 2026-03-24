---
name: agent-behavior-export
description: Use when asked to create or refresh agent prompt files for this OpenCode repo by extracting the effective behavior of the current runtime into repo-local prompt artifacts. Useful for updating agent/*.md or related prompt assets so deployed agents match actual working behavior.
---

# Agent Behavior Export

Encode real runtime behavior into repo-local prompt files.

## Inputs

- Active instructions from the current session
- Existing files under `agent/` and `prompts/`
- The export helper prompt at `prompts/agent-behavior-export-task.md`

## Workflow

1. Read the target agent prompt and adjacent prompt assets first.
2. Infer effective behavior from system, developer, repo, and tool-layer rules.
3. Preserve the repo's tone and structure instead of rewriting from scratch.
4. Update only the parts needed to reflect current behavior accurately.
5. Re-read the final file to ensure it matches the repo's conventions.

## Guardrails

- Keep the result specific to the actual runtime, not a generic assistant persona.
- Do not claim capabilities that depend on unavailable tools.
- Call out any behavior that cannot be fully encoded because it is platform-injected.
