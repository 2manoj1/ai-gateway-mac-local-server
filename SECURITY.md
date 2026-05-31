# Security Policy

## Supported Versions

This project is early-stage. Security fixes target the current `main` branch.

## Reporting a Vulnerability

Please do not open a public issue for a security vulnerability.

For the public GitHub repository, enable GitHub private vulnerability reporting
or add a private maintainer contact email before announcing a production-ready
release.

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
