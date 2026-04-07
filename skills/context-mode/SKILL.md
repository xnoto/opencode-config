---
name: context-mode
description: Mandatory context-protection routing rules for large output, web fetches, and analysis work.
---

## When to load

Load this skill at the start of the session whenever the `skill` tool is available, unless you are explicitly operating as the llama agent.

## Core rules

- Use `context-mode` to protect the context window whenever it is available.
- Do not use shell `curl`/`wget` or inline HTTP calls.
- For web pages, prefer `context-mode_ctx_fetch_and_index` and then `context-mode_ctx_search`.
- For sandboxed HTTP/API calls, use `context-mode_ctx_execute`.
- For commands likely to exceed 20 lines of output, prefer `context-mode_ctx_batch_execute` or `context-mode_ctx_execute` over direct shell.
- When reading files for analysis rather than editing, prefer `context-mode_ctx_execute_file`.
- For broad search output, prefer sandboxed `context-mode` execution over dumping raw grep results.

## Tool selection order

1. `context-mode_ctx_batch_execute`
2. `context-mode_ctx_search`
3. `context-mode_ctx_execute` / `context-mode_ctx_execute_file`
4. `context-mode_ctx_fetch_and_index`
5. `context-mode_ctx_index`

## Output discipline

- Keep responses under 500 words when practical.
- Write substantial artifacts to files rather than inline.
- Use descriptive source labels when indexing content.

## Maintenance commands

- `ctx stats`: call the stats tool and show the output verbatim.
- `ctx doctor`: call the doctor tool, run the returned shell command, display as a checklist.
- `ctx upgrade`: call the upgrade tool, run the returned shell command, display as a checklist.
