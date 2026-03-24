---
name: tmux-session-debugging
description: Use when the task involves inspecting or operating long-running local processes through tmux sessions, windows, or panes. Useful for checking app state, running commands in existing panes, capturing logs, or driving interactive terminal workflows without starting from scratch.
---

# Tmux Session Debugging

Use tmux as the first choice when a running local process already exists.

## Workflow

1. List sessions and locate the relevant session, window, and pane.
2. Capture pane output before sending commands so you understand current state.
3. Reuse the existing pane when practical instead of spawning duplicate processes.
4. For interactive tools, use raw mode or keystroke sending as needed.
5. Capture output again and summarize the observed result.

## Guardrails

- Avoid killing sessions or panes unless the user asks or the cleanup is obviously safe.
- Do not assume a pane is idle; inspect first.
- Prefer non-interactive commands when they can answer the question.

## Common uses

- Check whether a dev server is running
- Inspect recent logs from a pane
- Trigger a test run in an existing workspace session
- Debug a stuck interactive process
