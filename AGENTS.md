# AGENTS.md

## Required skill loading

- If the `skill` tool is available, agents must load the `context-mode` and `context7` skills at the start of the session before doing substantive work.

## MCP routing

Select by the named target environment. If it is unspecified, ask before querying or changing anything.

**Hatch** resources: use only `aws-staging`, `aws-prod`, `argocd-staging-eks`, `argocd-prod-eks`, and `grafana`. These are separate servers, so their tools are named `<server>_<tool>` with no extra prefix — Hatch Grafana is `grafana_query_prometheus`.

**Make IT Work Cloud** resources: use the direct `makeitwork-<integration>` servers — `makeitwork-apify`, `makeitwork-argocd`, `makeitwork-aws`, `makeitwork-aws-docs`, `makeitwork-cloudflare`, `makeitwork-context7`, `makeitwork-gcp`, `makeitwork-grafana`, `makeitwork-kubernetes`, `makeitwork-parallel-search`, `makeitwork-playwright`, `makeitwork-slidespeak`, `makeitwork-terraform-docs`, and `makeitwork-twilio-docs`. Each is its own remote server at `https://mcp-<integration>.makeitwork.cloud/mcp`, authenticating with `CF-Access-Client-*` headers referenced from the `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET` environment variables. Their tools are named `<server>_<tool>` — for example `makeitwork-grafana_query_prometheus`, `makeitwork-argocd_list_applications`, `makeitwork-kubernetes_pods_list`. AWS itself is one such server, reached as `makeitwork-aws_aws___<tool>`; the server is not AWS-specific despite that prefix. `github`, `hero-ssh`, and `codebase-memory` have no external endpoint and stay on internal or client-local transports.

**Environment-neutral** tooling also arrives through direct servers: `makeitwork-parallel-search_*` (web), `makeitwork-context7_*` (library docs), `makeitwork-aws-docs_*`, `makeitwork-terraform-docs_*`, `makeitwork-apify_*`, `makeitwork-cloudflare_*`, `makeitwork-gcp_*`, `makeitwork-playwright_*`, `makeitwork-slidespeak_*`, and `makeitwork-twilio-docs_*`. `opentofu-docs` is a standalone server.

Each integration is its own server entry again, so `mcp.makeitwork-<integration>.enabled` can enable or disable it individually per project or profile; the former aggregate `makeitwork` entry no longer exists. A project or profile can still deny one integration's tools instead: `"tools": { "makeitwork-apify_*": false }`.

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
- For AWS, Terraform, and OpenTofu documentation, use the specialized tools instead: `makeitwork-aws-docs_*`,
  `makeitwork-terraform-docs_*`, and `opentofu-docs_*`. For OpenCode configuration, use the checked-in schema and repository validation.

## MCP integration changes (gateway-first)

- New MCP servers belong in the `mcp-gateway` repo (`servers.json` entry on the next free 87xx localhost port, plus a POSIX `bin/<name>` wrapper when the server needs credentials). Agent configs in `opencode-config`, `codex-config`, `claude-config`, and project `opencode.json` files then point at `http://127.0.0.1:<port>/mcp` with `oauth: false`.
- The exceptions are the fourteen direct `makeitwork-<integration>` remote entries (one per external endpoint at `https://mcp-<integration>.makeitwork.cloud/mcp`, CF-Access headers from the environment) and the OAuth SaaS servers `linear` and `notion`. Do not add a second remote entry for a backend a direct `makeitwork-*` endpoint already serves, and never inline a secret value — headers reference environment variables only.
- Credentials for gateway wrappers come from `dotfiles` `encrypted_secrets.yaml.age` via `private_dot_shellenv.tmpl` (the `*_mcp_token` key convention); wrappers source `~/.shellenv` themselves. Secrets never appear in agent config repos.
- Disable-by-default in the global `opencode.json` (`enabled: false`); projects opt in. Keep `opencode-llama` opted out of non-essential servers.
- Project `opencode.json` files carry deltas only: configs deep-merge per server key, so an inherited server needs no project entry at all, `"name": { "enabled": true|false }` flips state, and full definitions (`type`/`url`/`command`) belong only to servers the global config does not define (e.g. a project-local stdio server).
- After gateway changes, the gateway service must be restarted and agents reloaded before the tools appear; service restarts require explicit user confirmation.

## Codebase Memory routing

- `codebase-memory` is a local, derived code-discovery index served by the gateway. Use it only for repositories below `~/git`, and index each repository explicitly rather than indexing the parent directory.
- The global server definition is disabled. An intended project opts in with only `"codebase-memory": { "enabled": true }`; do not duplicate the server URL or transport definition.
- Keep shared graph-artifact persistence disabled so repository source is not modified. The local index can be stale or incomplete; use GitHub MCP for exact file reads, remote branch heads, repository writes, and freshness-critical claims.
- The server has no credentials or OAuth flow. Its index updates local derived state, so preserve the normal confirmation boundary for tool calls that are not purely read-only.

## apify routing

- Apify (`makeitwork-apify_*` tools) is for structured marketplace and business-listing data that the free web tools cannot reach: Facebook Marketplace listings, Google Maps vendor/business discovery, and ecommerce price checks via `call-actor`. It arrives through its own direct `makeitwork-apify` server entry, so a project or profile can disable it via `mcp.makeitwork-apify.enabled`; keep the guardrail behavioural regardless: treat it as opt-in by judgement and fall back to the normal web stack unless the criteria below are met.
- Apify is pay-per-event with real money and returns bulk datasets. It is the LAST resort, not a search tool: exhaust context-mode fetch/index, Context7, and parallel-search first. Reach for Apify only when the target is login-walled or anti-bot (Facebook Marketplace, Google Maps) or when structured listing records are the actual deliverable.
- Every Apify call must be tight: set result limits (`resultsLimit`/`maxItems`), price filters, and location radius up front. Unbounded actor runs waste money and can blow the context window with dataset dumps.
- Prefer the pinned first-class tools (`facebook-marketplace-scraper`, `google-maps-scraper`) over `call-actor` discovery; use `search-actors`/`call-actor` only for actors not pinned in the config.
- Never put credentials, private URLs, or personal account cookies into actor inputs. Searches go out as generic buyer/research queries only.

## parallel-search routing

- `makeitwork-parallel-search_web_search` and
  `makeitwork-parallel-search_web_fetch` are the fallback
  for the open web. Lookup order: dedicated documentation MCPs, then Context7
  for any library or framework documentation, then context-mode fetch/indexing
  for known URLs, then parallel-search; prefer parallel-search over the
  built-in `webfetch` and `google_search` tools when available.
- Use `makeitwork-parallel-search_web_search` for general web discovery and current
  information — news, prices, listings, vendors, and similar open-web topics.
  "Current information" never includes library or framework documentation;
  that belongs to Context7 regardless of how the question is phrased. Search
  excerpts are usually sufficient; follow up with `makeitwork-parallel-search_web_fetch`
  only when excerpts are truncated, conflicting, or exact wording is required.
- Use `makeitwork-parallel-search_web_fetch` for known public URLs when context-mode is
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
