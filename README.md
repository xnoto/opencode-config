# opencode-config

Canonical OpenCode configuration consumed by `xnoto/dotfiles` as the
`~/.config/opencode` Git external with fast-forward-only updates.

## Bounded specialist subagents

Seven supplied-material specialists live in `agents/*.md`:

| Agent | Use |
| --- | --- |
| `adversarial-code-reviewer` | Independent completed-diff review before a PR or a requested second opinion. |
| `qa-engineer` | Acceptance-to-check coverage, test cases, and documentation adequacy. |
| `docs-writer` | Standalone documentation drafting; not agent policy, skills, or knowledge bases. |
| `infra-security-reviewer` | Infrastructure secret-handling, privilege, exposure, and supply-chain review. |
| `devops-engineer` | DESIGN/CHANGE review of CI, workflows, artifacts, runners, and integration contracts. |
| `release-engineer` | Actual release-contract, version, pin, generated-copy, and delivery-stage review. |
| `cloud-architecture-reviewer` | Preimplementation review of new/material cloud service, state, recovery, scaling, or cost decisions. |

The primary supplies the complete relevant evidence, intent, repository contracts,
producer-consumer context, and validation status. Missing essential inputs return
HOLD or BLOCKED; reviewers do not browse for substitutes. Use fresh reviewer
context and invoke roles selectively, not all seven on every change. Resolve
Critical/High findings or obtain an explicit owner waiver. Verdicts never authorize
merge, publication, deployment, installation, or live mutation. Models inherit the
parent; no chart provider pins are imported.

These native files are independently adapted from the roles in
[opencode-server](https://github.com/makeitworkcloud/charts/tree/70c96e408c6bc0e04532a055c8558a38c2d861be/opencode-server/files/agents).
Each config repository owns its copies; no generator or automatic synchronization
was introduced. The source chart, MCP endpoints, packages, and primary model
settings are unchanged.

`adversarial-code-reviewer` replaces `bullshit-detector`. The Claude primary
agent has been removed; the remaining primary agents, `security-auditor`,
`observability-debugger`, and provider-routing aliases are otherwise retained.
The security auditor handles broader repository/chezmoi hygiene; the infrastructure
reviewer assesses a supplied infrastructure diff.

### Native permissions and compatibility

The new definitions target [OpenCode V2](https://opencode.ai/v2/docs/agents), with
`mode: subagent` and a single native `permissions` rule denying every action and
resource. They have no model pin. They consume supplied evidence only and do not
load skills or call tools, even when ambient instructions normally route to them.

Remaining legacy definitions and `opencode.jsonc` are unchanged. V2 [supports legacy definitions](https://opencode.ai/v2/docs/migrate-v1);
the new V2 permission shape must not be used with V1, which may ignore its denies.
Installed client version and effective project overrides are separate verification
gates, not facts established by this repository.

### Usage

Ask the primary: "Use adversarial-code-reviewer on this completed change. Supply
the full diff, acceptance criteria, repository guidance, ownership/consumer map,
and available validation results; return ranked findings and remaining gates."
Do not ask a tool-denied reviewer to discover that evidence itself.

## Validation and delivery

The existing `Lint` workflow runs pre-commit on PRs and main pushes. The existing
frontmatter validator accepts legacy rules and native V2 permission lists; its
unit tests cover invalid rules and the seven-role deny-all roster. Source checks
do not prove native discovery, effective tool denial, model selection, or review
quality. No client tests or workstation installs are claimed.

Delivery stages: branch source and PR checks, confirmation-gated merge to main,
owner-run existing chezmoi external update, then a fresh session and controlled
role-discovery/tool-denial checks. A successful tracked Git external update removes
the old tracked reviewer file; unmanaged copies and other project definitions
remain outside that guarantee. No installation or restart is performed here.

## MCP source routing

`AGENTS.md` owns the shared task-to-source table for tool-capable agents.
General public-web discovery starts with parallel-search; dedicated docs and
workspace integrations retain their domains. Context-mode handles large output
and substantial known-page analysis, not web discovery. The startup skills defer
to that table. Built-in `websearch` and `webfetch` require approval as exceptional
fallbacks rather than silently competing with parallel-search. The seven
supplied-material reviewers remain tool-denied.

The existing global server enablement is preserved. Enabled configuration is not
proof of connectivity, permissions, or endpoint health. The config retains its
compatible legacy syntax; this change is not a native V2 migration.

### Source guards

Pre-commit runs `scripts/check-mcp-routing.py` and `tests/test_mcp_routing.py`.
The guards check parallel-search enablement, last-matching legacy permission
rules, approval-gated built-in fallbacks, and key instruction-table regressions.
They use source files only, make no endpoint calls, and do not prove effective
project permissions, instruction compliance, or runtime tool selection. A native
config migration must explicitly adapt these guards rather than silently skip
them.

### Controlled runtime checks

After an owner-approved deployment, use fresh sessions with the intended primary
agent and project configuration. Inspect tool traces, not just the final answer.
Catalog discovery may precede the expected evidence call but does not count as
that call. Do not query private workspaces or live environments merely to run a
test; those rows use supplied hypothetical scenarios until separately authorized.

| Prompt or scenario | Expected evidence route / behavior |
| --- | --- |
| Compare current public pricing for two products. | parallel-search `web_search`; no built-in search or browser search |
| Find the latest React API documentation. | Context7 resolve, then docs query; no general web search |
| Find AWS S3 documentation / Terraform provider docs / OpenTofu resource docs. | `aws-docs` / `terraform-docs` / `opentofu-docs`, respectively |
| Explain an OpenCode configuration setting. | OpenCode skill, official V2 docs, relevant source validation |
| Inspect a public repository's failing GitHub Actions run. | GitHub Actions readers, not web search or shell `gh` as the first route |
| Extract a focused passage from a known public URL. | parallel-search `web_fetch` with `urls`; no automatic second fetch |
| Analyze a long known public page across several questions. | context-mode fetch/index, then indexed search |
| Hypothetical: find a team decision or ticket. | Notion plus connector search for discussions / Linear for tickets; no public search |
| Hypothetical: check cluster health without naming an environment. | Clarify before any environment query |
| Hypothetical: parallel-search is unavailable. | Disclose limitation and request approval before built-in fallback; do not bypass a deny |
| Review a supplied diff using a supplied-material reviewer. | No tool calls or skill loading by that reviewer |
| Refactor a self-contained supplied function. | No unnecessary web or MCP calls |

Repeat the checks for tool-capable provider aliases when evaluating model-specific
compliance. Record configuration/version, selected agent, expected route, actual
tool names, approval/disclosure behavior, and pass/fail without storing credentials
or private payloads. Planning-only scenario responses are not live routing proof.
