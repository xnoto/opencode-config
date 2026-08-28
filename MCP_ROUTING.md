# MCP routing

For Hatch resources, use only `aws-staging`, `aws-prod`, `argocd-staging-eks`, `argocd-prod-eks`, and `grafana` (`grafana_*`). For Make IT Work Cloud resources, use only `makeitwork-aws`, `makeitwork-argocd`, `makeitwork-kubernetes`, and `makeitwork-grafana` (`makeitwork-grafana_*`). `apify`, `aws-docs`, `context7`, `parallel-search`, and `terraform-docs` are environment-neutral. Select by the named target environment; if it is unspecified, ask before querying or changing anything.
