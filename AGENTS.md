# Modes

| Mode | When | Action |
|------|------|--------|
| Investigate | Ambiguous requirements, unknown state | Gather evidence with tools, propose options |
| Troubleshoot | Something is broken or regressed | Find root cause, propose remediation |
| Implement | Clear requirements confirmed | Execute idempotently with minimal drift |

# Rules

- Check existence before create, Read before Edit
- `AGENTS.md` first, `CONTRIBUTING.md` second
- Ask before commit, `pre-commit` before commit
- ALL commits must follow Conventional Commits format (including merge commits)
- Never push to main branch, PR required
- PR summaries professional and concise, not overly worded

# Commit Approval

ALWAYS fully test and validate before asking to commit
Only commit/push when user explicitly requests: "commit", "push", "ship it"

# Don'ts

- Commit/push without explicit user approval
- Unilateral architectural decisions
- Describe past behavior leading up to a summary, rather than the current state
- Create commits that don't follow Conventional Commits format
