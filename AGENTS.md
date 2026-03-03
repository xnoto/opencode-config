# Modes

| Mode | When | Action |
|------|------|--------|
| Investigate | Ambiguous requirements, unknown state | Gather evidence with tools, propose options |
| Troubleshoot | Something is broken or regressed | Find root cause, propose remediation |
| Implement | Clear requirements confirmed | Execute idempotently with minimal drift |

# Rules

- Check existence before create; read before Edit
- `AGENTS.md` first, `CONTRIBUTING.md` second
- Ask before commit, `pre-commit` before commit
- Commits: [Conventional Commits](https://www.conventionalcommits.org/)
- Never push to main branch, PR's are required
- PR's summaries are professionally and concise, omiitting overly worded garbage

# Commit Approval

ALWAYS test and validate fully before asking to commit
Only commit/push when user explicitly requests: "commit", "push", "ship it"

# Don'ts

- Commit/push without explicit user approval
- Unilateral architectural decisions
- Describe past behavior leading up to a summary, rather than the current state.
