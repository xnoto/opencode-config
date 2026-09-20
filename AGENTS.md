# AGENTS.md

## Required skill loading

- If the `skill` tool is available, agents must load the `context-mode` and `context7` skills at the start of the session before doing substantive work.

## MCP routing

Select by the named target environment. If it is unspecified, ask before querying or changing anything.

**Hatch** resources: use only `aws-staging`, `aws-prod`, `argocd-staging-eks`, `argocd-prod-eks`, and `grafana`. These are separate servers, so their tools are named `<server>_<tool>` with no extra prefix — Hatch Grafana is `grafana_query_prometheus`.

**Make IT Work Cloud** resources: use the direct Make IT Work Cloud remote servers. Nine use bare integration names — `apify`, `aws-docs`, `context7`, `kubernetes`, `parallel-search`, `playwright`, `slidespeak`, `terraform-docs`, and `twilio-docs`. Five use the `makeitwork-` prefix: `makeitwork-argocd`, `makeitwork-aws`, and `makeitwork-grafana` retain it because their bare names collide with client integrations that represent other environments; `makeitwork-cloudflare` and `makeitwork-gcp` use it to make the Make IT Work Cloud scope explicit. These names target only Make IT Work Cloud resources, not other environments; the prefix is a naming distinction only, not a security boundary. All fourteen are the same kind of remote server at `https://mcp-<integration>.makeitwork.cloud/mcp`, authenticating with `CF-Access-Client-*` headers referenced from the `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET` environment variables. Their tools are named `<server>_<tool>` — for example `makeitwork-grafana_query_prometheus`, `makeitwork-argocd_list_applications`, `kubernetes_pods_list`, `aws-docs_search_documentation`. AWS itself is one such server, reached as `makeitwork-aws_aws___<tool>`; the server is not AWS-specific despite that prefix. `github`, `hero-ssh`, and `codebase-memory` have no external endpoint and stay on internal or client-local transports.

**Environment-neutral** tooling also arrives through direct servers: `parallel-search_*` (web), `context7_*` (library docs), `aws-docs_*`, `terraform-docs_*`, `apify_*`, `playwright_*`, `slidespeak_*`, and `twilio-docs_*`. `opentofu-docs` is a standalone server.

Each integration is its own server entry again, so `mcp.<server>.enabled` can enable or disable it individually per project or profile — for example `mcp.apify.enabled` or `mcp.makeitwork-grafana.enabled`; the former aggregate `makeitwork` entry no longer exists. A project or profile can still deny one integration's tools instead: `"tools": { "apify_*": false }`.

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
- Library and framework questions stay with Context7 even when phrased as "latest", "current", or "up to date" — freshness wording never reroutes documentation questions to web search.
- Resolve the Context7 library ID first, then query the docs.
- Do not use Context7 for AWS, Terraform, OpenTofu, or OpenCode documentation.
- For AWS, Terraform, and OpenTofu documentation, use the specialized tools instead: `aws-docs_*`, `terraform-docs_*`, and `opentofu-docs_*`. For OpenCode configuration, use the checked-in schema and repository validation.

## MCP integration changes (remote-first)

- Prefer an existing supported hosted remote endpoint appropriate to the same target environment over the local gateway, and verify the exact endpoint in canonical config; do not construct a hostname. Retain the local gateway for workstation-local or environment-specific requirements, or where no suitable hosted equivalent exists. For those services, use an `mcp-gateway` `servers.json` entry on the next free 87xx localhost port and a POSIX `bin/<name>` wrapper when credentials are needed; client configs point at `http://127.0.0.1:<port>/mcp` (with `oauth: false` in OpenCode).
- The fourteen direct Make IT Work Cloud entries are the established remote pattern, one per external endpoint at `https://mcp-<integration>.makeitwork.cloud/mcp`, with CF-Access headers from the environment: nine bare-named servers `apify`, `aws-docs`, `context7`, `kubernetes`, `parallel-search`, `playwright`, `slidespeak`, `terraform-docs`, and `twilio-docs`, plus five prefixed names `makeitwork-argocd`, `makeitwork-aws`, `makeitwork-grafana`, `makeitwork-cloudflare`, and `makeitwork-gcp`. The first three are prefixed because bare `argocd`, `aws`, and `grafana` are taken by client integrations for other environments; the latter two are prefixed to make the Make IT Work Cloud scope explicit. These names target only Make IT Work Cloud resources, not other environments; the prefix is a naming distinction only, not a security boundary. The OAuth SaaS servers `linear` and `notion` are also established remote integrations. Do not add a second remote entry for a backend one of these direct endpoints already serves, and never inline a secret value — headers reference environment variables only.
- Credentials for gateway wrappers come from `dotfiles` `encrypted_secrets.yaml.age` via `private_dot_shellenv.tmpl` (the `*_mcp_token` key convention); wrappers source `~/.shellenv` themselves. Secrets never appear in agent config repos.
- Disable-by-default in the global `opencode.json` (`enabled: false`); projects opt in. Keep `opencode-llama` opted out of non-essential servers.
- Project `opencode.json` files carry deltas only: configs deep-merge per server key, so an inherited server needs no project entry at all, `"name": { "enabled": true|false }` flips state, and full definitions (`type`/`url`/`command`) belong only to servers the global config does not define (e.g. a project-local stdio server).
- After gateway changes, the gateway service must be restarted and agents reloaded before the tools appear; service restarts require explicit user confirmation.

## Codebase Memory routing

`codebase-memory` is a local, derived code-discovery index served by the gateway. Use it only for repositories below `~/git`, and index each repository explicitly rather than indexing the parent directory. Keep shared graph-artifact persistence disabled so repository source is not modified. The local index can be stale or incomplete; use GitHub MCP for exact file reads, remote branch heads, repository writes, and freshness-critical claims.
