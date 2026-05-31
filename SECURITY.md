# Security Policy

## Supported Versions

This project is early-stage. Security fixes target the current `main` branch.

## Reporting a Vulnerability

Please do not open a public issue for a security vulnerability.

If this repository is published under your GitHub account, enable GitHub private
vulnerability reporting or add a private contact email here before announcing
the project publicly.

Include:

- Affected component
- Steps to reproduce
- Impact
- Suggested fix, if known

## Secrets

Never commit:

- `.env` files
- API keys
- database passwords
- PostgreSQL, Redis, or Qdrant volume data
- model files or generated private data
