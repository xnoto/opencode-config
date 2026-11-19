# AGENTS.md

## Source selection (all tool-capable agents)

Select the source before choosing how to reduce its output. This table is the
shared routing contract for primary agents and tool-capable subagents; skills
must not replace it with a different search order. Use tools when evidence is
needed, not merely because an integration is available.

| Task | First route |
| --- | --- |
| General public-web discovery, news, prices, comparisons, or current information | `parallel-search` `web_search` |
| Library/framework documentation, setup, API syntax, or examples | `context7`: resolve the library ID, then query docs |
| AWS / Terraform / OpenTofu documentation | `aws-docs` / `terraform-docs` / `opentofu-docs`, respectively |
| OpenCode behavior or configuration | Load the `opencode` skill; use official V2 docs and repository validation |
| Remote GitHub repository content, issues, PRs, releases, or CI | `github` by default for `Hatch1fy`; `makeitwork` and `xnoto` use the personal Git route below for their repositories |
| Internal decisions, discussions, or tickets | `notion` for workspace docs, the authorized discussion connector for conversations, and `linear` for tickets, when exposed |
| Substantial analysis of a known public page | `context-mode` fetch/index, then search the indexed source |
| Focused excerpts from a known public URL | `parallel-search` `web_fetch` |
| Browser interaction or a JavaScript-rendered page | `playwright`; retain approval gates for writes/uploads |
| Structured listing extraction unavailable through normal research | `apify`, subject to the paid-extraction rules below |
| Live cloud, cluster, or observability state | The named environment's MCPs below; clarify an unspecified target |
| Local repository discovery / large local analysis | Native file tools or an available `codebase-memory` index / `context-mode`, respectively |
| Presentation generation / terminal-session interaction | `slidespeak` / `tmux`, only for the requested task and with applicable approvals |

For general public-web discovery, use parallel-search `web_search` first. Do not
silently substitute built-in `websearch`, `webfetch`, browser search, or shell
HTTP. Dedicated documentation and workspace routes above take precedence for
their domains, including questions phrased as "latest" or "current".

If the preferred integration is absent, fails, or lacks access, disclose the
limitation and use an alternate authorized transport for the same target, such
as Git or `gh` for GitHub. An integration-specific failure is not a blanket
ban on other clients. Keep the intended account, environment, and approval
requirements; do not bypass an explicit denial of the operation itself. Before
using built-in `websearch` or `webfetch`, request explicit approval and respect
their permission gates. Clarify only when the resource target or account is
ambiguous.

## Verify session capabilities

Distinguish the source checkout, installed instructions and configuration, and
the current agent's live tool catalog. A checked-in or installed entry is not
proof that the session loaded it; catalog exposure is not proof of authorization
or a successful call. Inspect the live schema, and verify only the operations
needed for the task. If an OAuth connector is configured but not exposed, report
that limitation; do not infer the cause or start sign-in without direction.
Editing this checkout does not update installed files or the running session.

## Required skill loading

- If the `skill` tool is available, tool-capable agents must load `context-mode`
  and `context7` at the start of the session before substantive work. The seven
  supplied-material specialists below are exempt. A loaded skill does not make
  its integration available.

## MCP routing

For environment-specific resources, select by the named target environment. If
it is unspecified, ask before querying or changing those resources. Public
documentation and web research are environment-neutral.

| Scope | Configured server keys |
| --- | --- |
| Hatch | `aws-staging`, `aws-prod`, `kubernetes-staging-eks`, `kubernetes-prod-eks`, `argocd-staging-eks`, `argocd-prod-eks`, `grafana` |
| Make IT Work Cloud resources | `makeitwork-argocd`, `makeitwork-aws`, `makeitwork-cloudflare`, `makeitwork-gcp`, `makeitwork-grafana`, `makeitwork-kubernetes` |
| General tooling hosted by Make IT Work Cloud | `apify`, `aws-docs`, `context7`, `parallel-search`, `playwright`, `slidespeak`, `terraform-docs` |
| Other remote services | `opentofu-docs`; `linear` and `notion` use OAuth |
| Workstation tooling | `github`, `tmux`, and `codebase-memory` through the loopback gateway; `context-mode` is a local process |

Use only the matching scope for live environment access. The two Hatch Kubernetes
servers use fixed contexts; neither is `makeitwork-kubernetes`. The `makeitwork-`
prefix distinguishes client-side server names; it does not enforce authorization
or form part of the endpoint hostname. The thirteen hosted entries use
`CF-Access-Client-*` headers via `CF_ACCESS_CLIENT_ID` and
`CF_ACCESS_CLIENT_SECRET` environment references. Use the exact URL in
`opencode.jsonc`, not a hostname derived from the server key.

The checked-in `opencode.jsonc` currently uses compatible legacy configuration
syntax and enables all 27 configured servers. A project or profile may restrict
them. Check effective configuration and the live catalog rather than assuming
that a configured server is connected, permitted, or healthy. If a Hatch AWS
route is missing, use an authorized alternate for the same Hatch account and
environment, never `makeitwork-aws`. Preserve the existing syntax unless a
migration is requested; native V2 uses different server and permission shapes.

## Code Mode discovery and invocation

- Names such as `parallel-search_web_search` are normalized permission names,
  not necessarily callable paths. MCP tools in Code Mode are reached through
  `execute`, not through the native shell or a context-mode subprocess.
- Inside `execute`, discover the intended namespace with a bounded catalog
  query, for example `search({ namespace: "parallel-search", limit: 2 })`.
  Inspect the returned `path` and `signature`, then call that exact path with
  its declared arguments. For example, the returned path can be
  `tools["parallel-search"].web_search(...)`; do not assume that path in another
  client or invent flattened function names.
- Catalog search discovers tools; it does not search the web or satisfy a
  research task. Follow discovery with the selected tool call when evidence is
  needed. Avoid broad catalog dumps, especially for large integrations.
- If the client exposes native MCP tools instead, use the actual exposed names.
  Neither discovery nor Code Mode grants permission to bypass approval gates.

## GitHub and Git credential routing

- **Default — Hatch work:** use the `github` MCP for `Hatch1fy` GitHub work,
  including `actions_list` and `actions_get` for CI. The client uses the
  loopback gateway on port 8767 without token headers. The gateway owns its
  Hatch-scoped credential; don't export, swap, or reuse it for personal work.
  If the MCP cannot perform the operation, use Git or `gh` with an authorized
  Hatch identity for the same organization and disclose the fallback.
- **Personal repositories — `makeitwork` and `xnoto` agents:** use the Git CLI
  as `env -u GITHUB_TOKEN git ...` for repository operations, including fetch,
  commit, and push. This removes the Hatch SSO token from the command's
  environment; it does not by itself choose a personal SSH key or credential
  helper. Verify account/remote routing without printing credentials.
  Do not use the Hatch MCP for these repositories, even if it can read public
  content. Git does not handle issues, PRs, or Actions; when needed, use only a
  user-approved route authenticated to the personal account.
- Verify the target owner and remote before remote operations. This split
  selects the correct identity; it does not authorize committing, pushing,
  publishing, or bypassing tool permissions or branch protection.

## context-mode routing

- Use `context-mode` when output reduction is needed. It governs output handling, not source selection; use the source-selection table first.
- Do not use shell `curl` or `wget`, and do not make inline HTTP calls from shell commands.
- For substantial analysis of a known public page, prefer `context-mode_ctx_fetch_and_index`, then `context-mode_ctx_search`. Do not fetch pages again when the selected search tool's excerpts already answer the question. Index only non-sensitive material; indexing can create local derived state.
- Do not use `context-mode_ctx_execute` for HTTP calls or to invoke MCP tools. Keep network research on the selected documentation, search, or public-page fetch tool; subprocess execution is not a security boundary.
- For read-only commands likely to produce more than about 20 lines of output, prefer `context-mode_ctx_batch_execute` or `context-mode_ctx_execute` over direct shell.
- When reading files for analysis rather than editing, prefer `context-mode_ctx_execute_file`.
- For broad local search output, prefer context-mode output reduction over dumping raw grep results into context.
- Within context-mode, choose the operation that fits: batch related local commands, search already indexed sources, execute local analysis, or fetch/index a known public page. This is not a web-search fallback sequence.
- If context-mode is unavailable for local inspection, report it and use bounded native file reads/search when permitted. Its execution tools are not a sandbox or an approval bypass.

## context-mode execution safety

- Before every `context-mode_ctx_execute`, `context-mode_ctx_execute_file`, or `context-mode_ctx_batch_execute` call, state the specific task, target, why context-mode is needed, expected side effects, and whether the operation is read-only.
- Keep approval-bearing code human-reviewable: at most 25 non-blank lines and 2,000 characters per script or batch command. Do not use minified, encoded, generated, downloaded, or otherwise opaque payloads; nested interpreters, heredocs, and hidden wrapper scripts are prohibited.
- If more logic is required, write a clearly named script with the normal file-editing tool, show and validate its diff, obtain any required approval, then invoke it with a short transparent command. Do not generate and execute the script inside one context-mode call.
- Set a precise `intent` for `context-mode_ctx_execute` and `context-mode_ctx_execute_file`. For `context-mode_ctx_batch_execute`, use descriptive labels and queries that identify what each command is checking.
- Use context-mode execution only for read-only local inspection, analysis, and output reduction. Never use it for deployments, infrastructure or cluster mutations, authenticated write APIs, commits, pushes, uploads, service actions, credential changes, or any operation that would otherwise require approval through another command or MCP tool.
- Do not combine credential or secret reads with network access in context-mode. Use a normal authorized client for network fallbacks; context-mode execution is for local inspection only.

## context7 routing

- If a dedicated MCP documentation integration already exists for a technology, prefer that tool before Context7.
- Use Context7 proactively for library and framework documentation, setup, configuration, and code examples.
- Library and framework questions stay with Context7 even when phrased as "latest", "current", or "up to date" — freshness wording never reroutes documentation questions to web search.
- Resolve the Context7 library ID first, then query the docs.
- Do not use Context7 for AWS, Terraform, OpenTofu, or OpenCode documentation.
- For AWS, Terraform, and OpenTofu documentation, use the specialized tools instead: `aws-docs_*`,
  `terraform-docs_*`, and `opentofu-docs_*`. For OpenCode configuration, use the
  `opencode` skill and official V2 docs for behavior; use repository checks to
  validate the checked-in form, not to infer native V2 syntax.

## MCP integration changes (remote-first)

- Keep `open-cursor` out of the global plugin list: it was removed after expanding the direct tool catalog and triggering startup compaction. Use a separate Cursor profile if needed.

- Prefer an existing supported hosted remote endpoint appropriate to the same target environment over the local gateway, and verify the exact endpoint in canonical config; do not construct a hostname. Retain the local gateway for workstation-local or environment-specific requirements, or where no suitable hosted equivalent exists. For those services, use an `mcp-gateway` `servers.json` entry on the next free 87xx localhost port and a POSIX `bin/<name>` wrapper when credentials are needed; client configs point at `http://127.0.0.1:<port>/mcp` (with `oauth: false` in OpenCode).
- Do not add a second remote entry for an existing backend. Keep secret values
  out of agent config repos: hosted headers use environment references, OAuth
  credentials are managed outside config, and gateway wrappers that need
  credentials follow the `mcp-gateway` and `dotfiles` contracts. Do not read or
  export those credentials to check the routing.
- New integrations should be disabled by default until explicitly approved. This does not describe the existing globally enabled set; do not silently disable it. Keep `opencode-llama` opted out of non-essential servers.
- Project `opencode.json(c)` files should contain only intended overrides. Compare canonical global and project configuration first, use exact server keys and permission namespaces, and verify merge behavior against the active version before changing server definitions. Do not assume legacy and native V2 overrides merge identically.
- After applying gateway changes, follow the gateway's reload procedure and verify tool exposure in a fresh OpenCode session. Applying installed config or restarting services requires explicit user confirmation.

## Persistent memory (opencode-mem)

- `opencode.jsonc` lists `opencode-mem` as a plugin, not an MCP server. The
  checked-in `opencode-mem.jsonc` defaults to manual use: automatic capture,
  profile/chat injection, compaction reinjection, and the web explorer are off.
  Keep those defaults unless the user explicitly approves a change.
- Use the exposed `memory` tool when relevant prior project decisions, failed
  approaches, or durable preferences would materially help. In Code Mode, discover
  it as `memory` (not `opencode-mem`); `mode: "help"` checks the interface without
  searching memories. If unavailable, disclose that limitation; never invent a
  tool or claim retrieval/persistence.
- Search with focused technical keywords, explicit `scope: "project"`, and a small result limit. Verify retrieved facts against current source. Confirm the session is attached to the intended project; using file tools on a sibling repository does not retarget memory. Do not assume worktree or marker behavior across plugin versions.
- Persist only on an explicit user request or after approval of the proposed content and destination. Store concise durable findings, not raw output or transcripts. Exclude secrets, credentials, and sensitive personal/customer data. Apply the same rule to `profile` calls with `content`, which write preferences rather than merely reading them.
- Require explicit user intent for `all-projects` searches or user-profile access, and explicit approval for deletion, migration, import, or export. Exports are sensitive plaintext. Respect tool approval prompts; do not bypass them through direct database access, shell commands, or another transport. Local retrieval can still initialize storage or download the embedding model on first use.
- Use opencode-mem for durable cross-session knowledge, context-mode for working-context/output retrieval, and codebase-memory for code discovery. Keep stable operating rules in `AGENTS.md`; do not duplicate raw session captures across memory systems or require blanket startup searches/profile dumps.
- The safe-default validator checks this source checkout, not effective configuration in every project. Verify the installed plugin version and its global and project configuration precedence before claiming runtime safety. Obtain approval before applying changes or restarting OpenCode.

## Codebase Memory routing

- `codebase-memory` is a local, derived code-discovery index served by the gateway. Use it only for repositories below `~/git`, and index each repository explicitly rather than indexing the parent directory.
- The checked-in global server definition is enabled. Project restrictions and runtime availability can differ; inspect the live catalog and index status before relying on it. Do not create or refresh an index without the applicable confirmation.
- Keep shared graph-artifact persistence disabled so repository source is not modified. The index can be stale or incomplete: verify exact local text with native reads, and remote facts using the GitHub and Git routing above. An index result is not authorization to write to the repository.
- The server has no credentials or OAuth flow. Its index updates local derived state, so preserve the normal confirmation boundary for tool calls that are not purely read-only.

## apify routing

- Use Apify as a last resort for structured listings that ordinary research
  cannot deliver, not as a general search tool. Actor runs can incur charges and
  produce bulk datasets; observe applicable approvals and check pricing before running one.
- Prefer relevant dedicated Actor tools exposed by the live catalog; do not
  assume an Actor is pinned. Otherwise use bounded `search-actors`, then
  `fetch-actor-details` to check the input schema before `call-actor`.
- Use the Actor's actual limit fields, and price or radius filters where
  relevant. Do not start an unbounded run. Request only the necessary dataset
  rows and paginate when needed.
- Never put credentials, private URLs, or personal account cookies into actor inputs. Searches go out as generic buyer/research queries only.

## parallel-search routing

- parallel-search is the default for general public-web discovery, not a last
  resort after context-mode. Follow the source-selection table and fallback
  approval rule above; built-in `websearch` and `webfetch` are approval-gated.
- Use `parallel-search_web_search` for general web discovery and current
  information — news, prices, listings, vendors, and similar open-web topics.
  "Current information" never includes library or framework documentation;
  that belongs to Context7 regardless of how the question is phrased. Search
  excerpts are usually sufficient; follow up with `parallel-search_web_fetch`
  only when excerpts are truncated, conflicting, or exact wording is required.
- Use `parallel-search_web_fetch` for focused excerpts from known public URLs.
  Use context-mode fetch/index for substantial page analysis instead; do not
  call both by default. When using parallel-search fetch, pass user-provided
  URLs via the `urls` parameter (up to 20 per request).
- Generate one `session_id` per conversation (UUID or 32+ character hex) and
  reuse it for every parallel-search call; do not change it between turns. When
  supplying `model_name`, use the exact model slug from trusted session
  metadata; omit it if unknown rather than guessing.
- Give each search call one atomic `objective` plus at least one concise
  `search_queries` entry (2–3 related variants recommended). Group related
  queries or URLs under the same objective; run independent objectives
  concurrently instead of chaining calls.
- Keep fetches in excerpt mode (leave `full_content` off) unless the entire
  page is genuinely required; full-content fetches can exceed the context
  window.
- Do not use parallel-search for AWS, Terraform, OpenTofu, or OpenCode
  documentation, GitHub repository content, or any source a dedicated MCP
  covers. Fetch public URLs only; never attach credentials or private URLs.

## Bounded specialist delegation

Use the following supplied-material subagents selectively; do not run the whole
roster for every change:

- `adversarial-code-reviewer`: independent review of a completed non-trivial
  implementation before opening its PR, or an explicitly requested second opinion.
- `qa-engineer`: acceptance-to-check coverage, concrete test cases, and
  documentation adequacy; it does not implement tests or execute checks.
- `docs-writer`: standalone README, guide, and release-note drafting from
  supplied sources; not agent instructions, skills, policies, or knowledge bases.
- `infra-security-reviewer`: infrastructure-diff security review of privileges,
  secret handling, exposure, and supply-chain boundaries; never secret values.
- `devops-engineer`: DESIGN or CHANGE review of CI, workflow, artifact, runner,
  and delivery integration contracts; not implementation or live operations.
- `release-engineer`: versions, pins, generated copies, release documentation,
  and downstream stages against the actual repository release contract.
- `cloud-architecture-reviewer`: before implementing a new cloud service or
  material topology, state, recovery, scaling, service-selection, or cost change.

The primary gathers and supplies the complete relevant evidence, acceptance
criteria, repository guidance, producer-consumer context, and validation status.
These seven agents do not retrieve sources or load skills: their supplied-material
contract takes precedence over task-related tool/skill routing in this file.
Keep universal safety constraints, and never supply prohibited secret or state
material. Use fresh reviewer context, not a full-history fork of the authoring
session. Missing essential evidence must produce HOLD or BLOCKED, not invented
facts. Resolve Critical/High findings or obtain an explicit owner waiver; do not
treat a verdict as merge, publication, deployment, or runtime authorization.
The primary retains implementation and final decisions.

Check that the requested specialist is exposed before delegating. If unavailable,
report the limitation; do not pretend a named independent review occurred or
silently install/repair the client. The seven specialists have no model pins and
inherit the caller's model unless explicitly overridden. Other agents may have
their own model pins. Do not substitute provider aliases for specialist roles.
