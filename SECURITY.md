# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security vulnerabilities.

Report privately via GitHub's **"Report a vulnerability"** button under the
repository's **Security** tab (Security Advisories), or email
`security@zumud.com`.

Please include:
- a description of the issue and its impact,
- steps to reproduce (proof-of-concept if possible),
- affected component (backend / frontend / infra) and version/commit.

We aim to acknowledge reports within a few business days. Please allow a
reasonable period for a fix before any public disclosure.

## Scope

This repository contains application source only. Secrets and deployment
configuration are never committed; do not include real credentials in issues,
PRs, or reports. If you discover an exposed credential, treat it as sensitive
and report it privately rather than testing it.
