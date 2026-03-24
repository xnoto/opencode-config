---
name: context-mode-routing
description: Use when working in this OpenCode environment on tasks that may produce large command output, require repo analysis, or need web fetching. Enforce the repo's context-mode routing rules: prefer batch_execute/search/execute_file, avoid direct web fetching, avoid large raw shell output, and keep responses compact.
---

# Context Mode Routing

Apply the workspace routing rules before doing exploratory work.

## Core rules

- Prefer `context-mode_ctx_batch_execute` for repo inspection and multi-command gathering.
- Prefer `context-mode_ctx_execute_file` for analyzing large files without loading them into context.
- Prefer `context-mode_ctx_fetch_and_index` plus `context-mode_ctx_search` for web content.
- Use shell only for short-output commands and simple file-system or git operations.
- Do not use direct URL fetching tools in this workspace when the sandbox equivalent is available.

## Workflow

1. Decide whether the task is gather, follow-up search, processing, or web fetch.
2. Route to the matching context-mode tool first.
3. Read full files directly only when you need their contents in context for editing.
4. Keep summaries short and avoid dumping raw command output.

## Practical defaults

- For repo discovery, batch related commands into one `context-mode_ctx_batch_execute` call.
- For follow-up questions, query indexed results with one `context-mode_ctx_search` call containing all questions.
- For logs or bulky generated output, process in the sandbox and print only the needed summary.
- If a requested approach conflicts with the routing rules, explain the safer route briefly and continue.
