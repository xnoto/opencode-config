# Agent-local routing note

Context-mode and Context7 usage rules are defined in reusable skills and loaded by the non-llama agents from `agent/`.

- Non-llama agents are expected to load the `context-mode` and `context7` skills at session start when the skill tool is available.
- `llama.md` intentionally does not load or rely on those skills by default.
