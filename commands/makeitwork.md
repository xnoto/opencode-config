---
description: Load MakeItWork Cloud infra environment
agent: makeitwork
model: kimi-for-coding/k2p5
---

Load the working environment for `makeitworkcloud` GitHub org infrastructure tasks.

Required cluster context:
- Use context `api-makeitwork-cloud:6443` for both `kubectl` and `oc`.
- Verify local availability first:
  - `kubectl config get-contexts -o name | grep -Fx "api-makeitwork-cloud:6443"`
  - `oc config get-contexts -o name | grep -Fx "api-makeitwork-cloud:6443"`
- Switch context:
  - `kubectl config use-context api-makeitwork-cloud:6443`
  - `oc config use-context api-makeitwork-cloud:6443`

Reachability note:
- If the cluster is unreachable, check WARP and connect before retrying:
  - `warp-cli status`
  - `warp-cli connect`

This command uses the `makeitwork` agent, which enables OpenTofu MCP access.
