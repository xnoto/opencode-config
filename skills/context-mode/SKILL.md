---
name: context-mode
description: Mandatory context-protection routing rules for large output, web fetches, and analysis work.
---

## When to load

Load this skill at the start of the session whenever the `skill` tool is available.

## Core rules

- Follow the source-selection table in `AGENTS.md` first. Context-mode reduces output; it does not replace dedicated documentation, workspace, or search tools.
- For general public-web discovery, use parallel-search `web_search` first. Do not route web discovery through context-mode execution or browser search.
- Do not use shell `curl`/`wget` or inline HTTP calls.
- For substantial analysis of a known public page, use `context-mode_ctx_fetch_and_index` and then `context-mode_ctx_search`. Do not fetch again when search excerpts are sufficient; use parallel-search `web_fetch` for focused URL excerpts.
- Keep HTTP calls and MCP invocation out of `context-mode_ctx_execute`; use the selected dedicated integration instead. Execution is for read-only local analysis, not a security sandbox.
- For commands likely to exceed 20 lines of output, prefer `context-mode_ctx_batch_execute` or `context-mode_ctx_execute` over direct shell.
- When reading files for analysis rather than editing, prefer `context-mode_ctx_execute_file`.
- For broad search output, prefer sandboxed `context-mode` execution over dumping raw grep results.

## Choose an output-reduction operation

After source selection, use the operation that fits rather than trying these in sequence:

- `context-mode_ctx_batch_execute`: related read-only local commands.
- `context-mode_ctx_search`: retrieve already indexed evidence.
- `context-mode_ctx_execute` / `context-mode_ctx_execute_file`: read-only local analysis.
- `context-mode_ctx_fetch_and_index`: substantial analysis of a known public page.
- `context-mode_ctx_index`: retain non-sensitive material for subsequent queries.

Discover the live signatures through the client's exposed tools or Code Mode as
described in `AGENTS.md`; normalized names above are not assumed callable paths.
Before execution, state the task, target, reason for reduction, and expected side
effects. Keep scripts within 25 non-blank lines and 2,000 characters. Do not use
execution for writes, authenticated APIs, service actions, or approval bypasses.

## Output discipline

- Keep responses under 500 words when practical.
- Write substantial artifacts to files rather than inline.
- Use descriptive source labels when indexing content.

## Maintenance commands

- `ctx stats`: call the stats tool and report non-sensitive usage diagnostics.
- `ctx doctor` / `ctx upgrade`: inspect returned suggestions; do not automatically execute commands. Obtain explicit approval for maintenance side effects and use the normal approved execution path, never context-mode execution.
