---
name: context7
description: Mandatory library and framework documentation routing via Context7, with infrastructure doc exceptions.
---

## When to load

Load this skill at the start of the session whenever the `skill` tool is available.

## Core rules

- Use Context7 proactively for library/framework documentation, setup, configuration, and code examples.
- Prefer Context7 without waiting for the user to explicitly ask for it when accurate library docs are needed.
- Resolve the library ID first, then query docs.

## Do not use Context7 for

- AWS documentation
- Terraform documentation
- OpenTofu documentation
- OpenCode documentation

For those, use the specialized documentation tools instead.
