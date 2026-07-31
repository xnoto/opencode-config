# Agent Behavior Export Task

Run this task inside the coding assistant or CLI agent whose behavior should be exported. Inspect this repository's agent, prompt, and instruction conventions, then create or update the corresponding OpenCode agent definition so it mirrors the source client's effective behavior as closely as possible.

This task is intended to work when run by Claude Code, Kimi, Codex, or another coding assistant. The source client supplies the behavior profile and destination filename, but the generated file always executes as an OpenCode agent. The goal is not to dump hidden internal prompts verbatim, but to externalize the effective behavior that governs how the source client works in this session.

## Objective

Create or update the appropriate file under `agents/` for the source client, such as `agents/kimi.md`, `agents/claude.md`, or `agents/codex.md`, so it reproduces that client's working behavior as faithfully as possible within an OpenCode markdown agent file. The filename identifies the exported behavior profile; it does not change the OpenCode runtime or tool namespace.

## Requirements

- Read the repository first to understand its existing agent and instruction conventions.
- Match the repo's existing file format, frontmatter, structure, and tone for agent definitions.
- Treat the coding assistant running this task as the behavior source and OpenCode as the execution target.
- Infer your effective behavior from the instructions, policies, tool constraints, and working norms active in this session.
- Encode that behavior into the new agent file.
- Translate source-client tool behavior into exact, case-sensitive OpenCode tool identifiers. Preserve verified OpenCode built-in names such as `read`, `edit`, `write`, `apply_patch`, `glob`, `grep`, `bash`, `task`, `todowrite`, `question`, `skill`, `webfetch`, and `websearch`.
- Refer to configured MCP tools only by their exact OpenCode-exposed, server-prefixed names. Verify those names from the active OpenCode tool catalog, configuration, documentation, or established repository usage instead of guessing.
- Prefer implementation over explanation: actually write the file.
- Keep the resulting agent specific to your real behavior, not a generic assistant persona.

## Capture These Behaviors

Include guidance that reflects your current behavior in areas such as:

- coding style and engineering standards
- how you inspect and understand a codebase before editing
- tool usage preferences and search habits
- editing constraints and safety rules
- validation and testing expectations
- code review behavior
- communication style
- progress-update style while working
- response formatting conventions
- assumptions, escalation, and blocker handling
- limits where hidden runtime instructions cannot be fully reproduced in a repo-local file

## Process

1. Inspect the repository for existing agent files, instruction files, config files, and any agent-related conventions.
2. Derive your effective operating behavior from the instruction stack that governs this session.
3. Write the correct client-specific file under `agents/` in a way that fits the repository naturally.
4. Audit every tool identifier in the generated file against OpenCode's built-ins and configured MCP tools. Replace source-client aliases and remove any unverified tool names.
5. Validate the final frontmatter and structure against current OpenCode agent conventions and review the diff for accidental platform-specific claims.
6. Add a short `Limits` section explaining which parts of your behavior depend on hidden system prompts, platform policies, sandboxing, tool availability, or runtime permissions and therefore cannot be perfectly reproduced.

## Constraints

- Do not invent capabilities you do not actually have.
- Do not copy source-client tool identifiers such as `ReadFile`, `StrReplaceFile`, `Shell`, `SetTodoList`, `TaskCreate`, `AskUserQuestion`, `Agent`, `ToolSearch`, `shell_command`, or `update_plan` into the OpenCode agent file.
- Do not rename verified OpenCode tool identifiers to match the source client, model provider, or destination filename.
- If a source capability has no verified OpenCode equivalent, describe the behavior generically and document the limitation instead of inventing a tool name.
- Preserve the source client's working style without claiming that source-only tools, sandbox behavior, hooks, or platform capabilities are available inside OpenCode.
- Do not claim exact reproduction if platform-level behavior is not portable.
- Preserve the repository's style and conventions.
- Favor concrete, usable instructions over abstract principles.
- If exact internal instructions are inaccessible, capture only behavior supported by observed and active constraints; do not invent or reconstruct inaccessible prompt text.

## Preferred Framing

Use the idea of:

"Externalize the source client's effective instruction set into an OpenCode agent profile."

That framing is more portable across platforms than asking for a verbatim dump of hidden internal prompts.
