---
name: agent-hub-collaboration
description: Use when the user explicitly wants multi-agent collaboration or when work should be coordinated through the configured agent-hub MCP server. Covers agent registration, feature and task creation, delegation, sync, and message-based coordination across concurrent agent sessions.
---

# Agent Hub Collaboration

Coordinate work through agent-hub when multi-agent structure is part of the task.

## Workflow

1. Register the current agent if needed.
2. Create a feature when the work spans multiple related tasks.
3. Create tasks with clear delegations and scope boundaries.
4. Accept delegated work before executing it.
5. Sync periodically and post concise completion or blocker updates.

## Good practices

- Keep delegations narrow and testable.
- Share context that another agent can act on immediately.
- Use subtasks for concrete implementation steps, not vague reminders.
- Report blockers early with the exact missing dependency.

## Guardrails

- Do not use agent-hub for simple single-agent work.
- Do not create extra coordination overhead when direct execution is faster.
