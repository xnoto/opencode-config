---
name: context7
description: Mandatory library and framework documentation routing via Context7, with infrastructure doc exceptions.
---

## When to load

Load this skill at the start of the session whenever the `skill` tool is available.

## Core rules

- Follow the source-selection table in `AGENTS.md`; dedicated documentation integrations take precedence for their domains.
- Use Context7 proactively for library/framework documentation, setup, configuration, and code examples.
- Prefer Context7 without waiting for the user to explicitly ask for it when accurate library docs are needed.
- Resolve the library ID first, then query docs.
- "Latest" or "current" library documentation still belongs here, not in general web search. General public-web discovery belongs to parallel-search `web_search`, not Context7.
- If the selected documentation integration is unavailable or fails, disclose that limitation. Do not silently substitute built-in `websearch` or `webfetch`; follow the fallback approval rule in `AGENTS.md`.

## Do not use Context7 for

- AWS documentation
- Terraform documentation
- OpenTofu documentation
- OpenCode documentation

For AWS, Terraform, and OpenTofu, use `aws-docs`, `terraform-docs`, and
`opentofu-docs`, respectively. For OpenCode, load the `opencode` skill, consult
official V2 documentation, and use repository validation for config changes.
