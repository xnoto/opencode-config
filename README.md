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

`adversarial-code-reviewer` replaces `bullshit-detector`, including its reference
in `agents/claude.md`. The existing primary agents, `security-auditor`,
`observability-debugger`, and provider-routing aliases are otherwise retained.
The security auditor handles broader repository/chezmoi hygiene; the infrastructure
reviewer assesses a supplied infrastructure diff.

### Native permissions and compatibility

The new definitions target [OpenCode V2](https://opencode.ai/v2/docs/agents), with
`mode: subagent` and a single native `permissions` rule denying every action and
resource. They have no model pin. They consume supplied evidence only and do not
load skills or call tools, even when ambient instructions normally route to them.

Existing legacy definitions and `opencode.json` remain unchanged apart from the
renamed reviewer reference. V2 [supports legacy definitions](https://opencode.ai/v2/docs/migrate-v1);
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
