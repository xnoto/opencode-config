---
name: skill-smith
description: Design, scaffold, and validate OpenCode skills using Agent Skills conventions. Use when user asks to create, improve, migrate, or debug a skill, SKILL.md, trigger phrases, or skill loading behavior.
---

# Skill Smith

## Objective

Produce high-signal, reusable skills with clear triggers, deterministic workflows, and minimal context waste.

## Inputs To Collect

1. Scope: global skill (`~/.config/opencode/skills/`) or project skill (`.opencode/skills/`).
2. Skill intent: what problem it solves.
3. Trigger language: exact user phrases that should activate the skill.
4. Risk profile: whether tool actions should be constrained or approval-gated.

## Build Workflow

1. Create folder `<skill-name>/` where `<skill-name>` is kebab-case.
2. Create `SKILL.md` with YAML frontmatter:
   - `name` must match folder name.
   - `description` must include what + when + trigger phrases.
3. Add body sections:
   - Scope and assumptions.
   - Step-by-step workflow with explicit checks.
   - Output requirements.
   - Safety and rollback notes where relevant.
4. Add `references/` documents only for detail that should be loaded on demand.
5. If deterministic checks are needed, add `scripts/` and instruct the agent to run them.

## Trigger Quality Rules

- Include positive triggers: terms users will actually type.
- Avoid vague descriptions like "helps with infra".
- Avoid overtriggering by naming context and exclusions.

## Validation Checklist

Run these checks before finalizing:

1. Discovery checks:
   - Path is one of:
     - `~/.config/opencode/skills/<name>/SKILL.md`
     - `.opencode/skills/<name>/SKILL.md`
     - `.claude/skills/<name>/SKILL.md`
     - `.agents/skills/<name>/SKILL.md`
2. Frontmatter checks:
   - `name` is kebab-case and matches folder.
   - `description` includes explicit trigger phrases.
3. Behavior checks:
   - Relevant prompt should load skill.
   - Unrelated prompt should not load skill.
4. Execution checks:
   - Commands are valid and idempotent where possible.
   - Risky actions include confirmation and rollback guidance.
5. Validator check (deterministic):
   - If available, run `skills-ref validate <skill-dir>`.
   - Do not mark complete until validation passes.
   - If unavailable, state "validator unavailable" and continue checklist-only.

## Minimal Template

```yaml
---
name: your-skill-name
description: What it does and when to use it. Include trigger phrases users say.
---

# Your Skill

## Scope

## Workflow
1. Step one.
2. Step two.

## Output Requirements

## Safety
```
