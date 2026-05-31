# Open Source Maintenance Checklist

Use this checklist before each public release or major documentation refresh:

- Confirm `.env` files are ignored.
- Confirm no secrets are staged.
- Confirm GitHub URLs point to `2manoj1/ai-gateway-mac-local-server`.
- Choose and review the license.
- Run `make api-check`.
- Run `git status --short`.
- Confirm the GitHub repository is reachable.
- Confirm `main` is pushed.
- Confirm branch protection and secret scanning are enabled on GitHub.

## Recommended GitHub Settings

- Enable Dependabot alerts.
- Enable secret scanning.
- Enable private vulnerability reporting.
- Require the CI workflow before merging.
- Protect the default branch.

## Repository

<https://github.com/2manoj1/ai-gateway-mac-local-server>
