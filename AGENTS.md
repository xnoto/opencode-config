# AGENTS.md

## Required skill loading

- If the `skill` tool is available, non-llama agents must load the `context-mode` and `context7` skills at the start of the session before doing substantive work.
- `agents/llama.md` intentionally opts out of these skills and should keep that override.

## context-mode routing

- Use `context-mode` whenever it is available to protect the context window.
- Do not use shell `curl` or `wget`, and do not make inline HTTP calls from shell commands.
- For web pages, prefer `context-mode_ctx_fetch_and_index`, then `context-mode_ctx_search`.
- For sandboxed HTTP or API calls, use `context-mode_ctx_execute`.
- For commands likely to produce more than about 20 lines of output, prefer `context-mode_ctx_batch_execute` or `context-mode_ctx_execute` over direct shell.
- When reading files for analysis rather than editing, prefer `context-mode_ctx_execute_file`.
- For broad search output, prefer sandboxed `context-mode` execution over dumping raw search results into context.
- Tool selection order: `context-mode_ctx_batch_execute`, `context-mode_ctx_search`, `context-mode_ctx_execute` / `context-mode_ctx_execute_file`, `context-mode_ctx_fetch_and_index`, then `context-mode_ctx_index`.

## context7 routing

- If a dedicated MCP documentation integration already exists for a technology, prefer that tool before Context7.
- Use Context7 proactively for library and framework documentation, setup, configuration, and code examples.
- Resolve the Context7 library ID first, then query the docs.
- Do not use Context7 for AWS, Terraform, OpenTofu, or OpenCode documentation.
- For those exceptions, use the specialized documentation tools instead: `aws-docs`, `terraform-docs`, `opentofu-docs`, and `opencode-docs`.
