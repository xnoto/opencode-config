---
description: Create a MakeItWork AWS Secrets Manager secret from a local file.
---

Create an AWS Secrets Manager secret from a local private-key or credential file.

Arguments: `$ARGUMENTS`, in the required form `<secret-name> <file-path>`.

Use `aws --profile makeitwork --region us-west-2` for all AWS CLI calls. Do not use an AWS MCP tool for the upload because its CLI wrapper does not allow local-file references.

Workflow:

1. If both arguments are not present, ask the user for the secret name and local file path. Do not infer either.
2. Verify that the file exists and is a regular file. Never print, read into chat, log, or otherwise expose its contents.
3. Run `aws --profile makeitwork --region us-west-2 secretsmanager describe-secret --secret-id <secret-name>` to check for an existing secret.
4. If it exists, stop and report its ARN. Do not update, overwrite, or delete it unless the user explicitly asks.
5. If it does not exist, create it with `aws --profile makeitwork --region us-west-2 secretsmanager create-secret --name <secret-name> --secret-string file://<file-path>`. Add a concise description only if the user provided one.
6. Report only the secret name, region, ARN, and version ID. Never report the secret value.

Treat the file as sensitive throughout. If AWS returns an error, report the error without retrying destructive or overwrite operations.
