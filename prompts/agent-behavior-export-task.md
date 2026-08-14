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
- Translate every source-client tool reference into an exact, case-sensitive tool identifier exposed by the target OpenCode runtime. Build an explicit source-to-target mapping while drafting, including ordinary operations such as listing a directory; do not assume that similarly named capabilities use the same identifier in Codex, Claude Code, Kimi, or OpenCode.
- Treat the active OpenCode tool catalog as authoritative. The commonly available built-ins include `read`, `edit`, `write`, `glob`, `grep`, `list`, `bash`, `task`, `todowrite`, `question`, `skill`, `webfetch`, and `websearch`, but availability and additional identifiers vary by installation. Mention a tool by name only after verifying that exact identifier in the target runtime - acceptable verification sources are the repository's `opencode.json` permission keys, the OpenCode documentation (or `opencode-docs` MCP), and existing agent files known to work in this installation.
- Refer to configured MCP tools only by their exact OpenCode-exposed, server-prefixed names. Verify those names from the active OpenCode tool catalog, configuration, documentation, or established repository usage instead of guessing.
- Translate source-client planning behavior into ordinary instructions, todo usage, or read-only permissions as appropriate. Do not assume the target OpenCode installation has a plan/apply switch, do not instruct the exported agent to change runtime modes, and do not preserve source-only planning commands as tool names.
- Prefer implementation over explanation: actually write the file.
- Keep the resulting agent specific to your real behavior, not a generic assistant persona.

## Capture These Behaviors

Include guidance that reflects your current behavior in areas such as:

- coding style and engineering standards
- how you inspect and understand a codebase before editing
- tool usage preferences and search habits
- how source tool names map to tools actually exposed by OpenCode
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
4. Make a source-to-OpenCode capability table for your own audit. Cover every named source tool and every implied operation, including directory listing, file search, content search, reading, editing, shell execution, task delegation, user questions, and task tracking. The table is working material and need not appear in the generated agent file.
5. Audit every resulting tool identifier against the active OpenCode built-ins and configured MCP tools. Replace source-client aliases, remove unverified names, and describe capabilities generically when no target tool is verified.
6. Remove assumptions about source-client plan/apply modes. Express read-only planning as behavior or permissions, while leaving agent selection and runtime mode changes to OpenCode and the user.
7. Validate the final frontmatter and structure against current OpenCode agent conventions and review the diff for accidental platform-specific claims.
8. Add a short `Limits` section explaining which parts of your behavior depend on hidden system prompts, platform policies, sandboxing, tool availability, or runtime permissions and therefore cannot be perfectly reproduced.

## Constraints

- Do not invent capabilities you do not actually have.
- Do not copy source-client tool identifiers such as `ReadFile`, `StrReplaceFile`, `Shell`, `SetTodoList`, `TaskCreate`, `AskUserQuestion`, `Agent`, `ToolSearch`, `shell_command`, or `update_plan` into the OpenCode agent file.
- Do not infer that a shell command such as `ls` or a client UI action is an OpenCode tool identifier merely because the operation exists. If directory listing has no separately verified target tool, express the intent generically or use the verified target mechanism rather than inventing a name.
- Do not rename verified OpenCode tool identifiers to match the source client, model provider, or destination filename.
- Do not claim or require a plan/apply mode toggle. An OpenCode installation may provide separately selectable agents with different permissions, but the exported agent cannot assume that such agents exist or switch itself between them.
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
