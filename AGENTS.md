# AGENTS.md

## Required skill loading

- If the `skill` tool is available, agents must load the `context-mode` and `context7` skills at the start of the session before doing substantive work.

## context-mode routing

- Use `context-mode` whenever it is available to protect the context window.
- Do not use shell `curl` or `wget`, and do not make inline HTTP calls from shell commands.
- For web pages, prefer `context-mode_ctx_fetch_and_index`, then `context-mode_ctx_search`.
- For read-only HTTP or public API analysis that needs code, use `context-mode_ctx_execute` only under the execution-safety rules below. Its subprocess has full network access and is not a security boundary.
- For read-only commands likely to produce more than about 20 lines of output, prefer `context-mode_ctx_batch_execute` or `context-mode_ctx_execute` over direct shell.
- When reading files for analysis rather than editing, prefer `context-mode_ctx_execute_file`.
- For broad search output, prefer sandboxed `context-mode` execution over dumping raw search results into context.
- Tool selection order: `context-mode_ctx_batch_execute`, `context-mode_ctx_search`, `context-mode_ctx_execute` / `context-mode_ctx_execute_file`, `context-mode_ctx_fetch_and_index`, then `context-mode_ctx_index`.

## context-mode execution safety

- Before every `context-mode_ctx_execute`, `context-mode_ctx_execute_file`, or `context-mode_ctx_batch_execute` call, state the specific task, target, why context-mode is needed, expected side effects, and whether the operation is read-only.
- Keep approval-bearing code human-reviewable: at most 25 non-blank lines and 2,000 characters per script or batch command. Do not use minified, encoded, generated, downloaded, or otherwise opaque payloads; nested interpreters, heredocs, and hidden wrapper scripts are prohibited.
- If more logic is required, write a clearly named script with the normal file-editing tool, show and validate its diff, obtain any required approval, then invoke it with a short transparent command. Do not generate and execute the script inside one context-mode call.
- Set a precise `intent` for `context-mode_ctx_execute` and `context-mode_ctx_execute_file`. For `context-mode_ctx_batch_execute`, use descriptive labels and queries that identify what each command is checking.
- Use context-mode execution only for read-only local inspection, analysis, and output reduction. Never use it for deployments, infrastructure or cluster mutations, authenticated write APIs, commits, pushes, uploads, service actions, credential changes, or any operation that would otherwise require approval through another command or MCP tool.
- Do not combine credential or secret reads with network access in a context-mode execution. Never use context-mode to bypass a denial, approval gate, sandbox, authentication failure, or a dedicated tool's permission policy.

## context7 routing

- If a dedicated MCP documentation integration already exists for a technology, prefer that tool before Context7.
- Use Context7 proactively for library and framework documentation, setup, configuration, and code examples.
- Resolve the Context7 library ID first, then query the docs.
- Do not use Context7 for AWS, Terraform, OpenTofu, or OpenCode documentation.
- For those exceptions, use the specialized documentation tools instead: `aws-docs`, `terraform-docs`, `opentofu-docs`, and `opencode-docs`.

## parallel-search routing

- `parallel-search_web_search` and `parallel-search_web_fetch` are the fallback
  for the open web. Prefer dedicated documentation MCPs, Context7, and
  context-mode fetch/indexing first; prefer parallel-search over the built-in
  `webfetch` and `google_search` tools when available.
- Use `parallel-search_web_search` for general web discovery and current
  information not covered by a dedicated tool. Search excerpts are usually
  sufficient; follow up with `parallel-search_web_fetch` only when excerpts
  are truncated, conflicting, or exact wording is required.
- Use `parallel-search_web_fetch` for known public URLs when context-mode is
  unavailable or direct retrieval is sufficient. Always pass URLs the user
  provides via the `urls` parameter (up to 20 per request).
- Generate one `session_id` per conversation (UUID or 32+ character hex) and
  reuse it for every parallel-search call; do not change it between turns.
- Give each search call one atomic `objective` plus 2-3 concise related
  `search_queries`; make separate calls for separate questions instead of
  chaining searches.
- Keep fetches in excerpt mode (leave `full_content` off) unless the entire
  page is genuinely required; full-content fetches can exceed the context
  window.
- Do not use parallel-search for AWS, Terraform, OpenTofu, or OpenCode
  documentation, GitHub repository content, or any source a dedicated MCP
  covers. Fetch public URLs only; never attach credentials or private URLs.
