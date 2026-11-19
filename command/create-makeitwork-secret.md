---
description: Create a MakeItWork AWS Secrets Manager secret from a local file.
---

Create an AWS Secrets Manager secret from a local private-key or credential file.

Arguments: `$ARGUMENTS`, in the required form `<secret-name> <file-path>`.

Use `aws --profile makeitwork --region us-west-2` for all AWS CLI calls. Use only the local CLI to send the file directly to Secrets Manager; never put its contents into tool arguments, transcripts, or an MCP call.

Workflow:

1. If both arguments are not present, ask the user for the secret name and local file path. Do not infer either.
2. Verify that the file exists and is a regular file without reading its contents. Accept confirmed text input only. Pass the name and file URI as individually quoted arguments; treat user input as data, not shell syntax.
3. Use `sts get-caller-identity --query Account --output text` with the same profile and region. Compare with the expected account supplied or confirmed by the user. Stop if unknown or mismatched.
4. Check with `secretsmanager describe-secret --secret-id`, passing the name as one argument. If found, stop and report its ARN. Continue only on an explicit `ResourceNotFoundException`; stop on any other failure.
5. Immediately before creating, ask the user to confirm the exact path, secret name, account and region, and that AWS will receive the file. Stop if confirmation is missing or the target, profile, or file has changed; recheck and request fresh confirmation. Only then use `secretsmanager create-secret --name` with the name and `--secret-string` with a single quoted `file://` URI for the confirmed path. Do not update or delete an existing secret.
6. Report only the secret name, region, ARN, and version ID. Never report the secret value.

Do not use debug mode, shell tracing, or raw error dumps. Report a sanitized error code or summary and stop. Do not retry an ambiguous upload failure.
