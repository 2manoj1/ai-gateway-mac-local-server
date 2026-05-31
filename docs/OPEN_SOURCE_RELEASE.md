# Open Source Release Checklist

Before publishing:

- Confirm `.env` files are ignored.
- Confirm no secrets are staged.
- Replace placeholder GitHub URLs in docs.
- Choose and review the license.
- Run `make api-check`.
- Run `git status --short`.
- Create the GitHub repository.
- Push the `main` branch.
- Enable branch protection and secret scanning on GitHub.

## Recommended GitHub Settings

- Enable Dependabot alerts.
- Enable secret scanning.
- Enable private vulnerability reporting.
- Require the CI workflow before merging.
- Protect the default branch.
