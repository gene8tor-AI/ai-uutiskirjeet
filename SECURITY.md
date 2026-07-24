# Security policy

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability or exposed secret.

Report the finding privately to the repository owner with:

- affected repository and component;
- a short reproduction description;
- potential impact;
- whether credentials, personal data, or production systems may be involved.

## Secrets

- Store secrets only in the platform's secret manager or approved environment-variable store.
- Do not commit `.env` files or credentials.
- If a secret may have been exposed, revoke or rotate it immediately and record the remediation in the operational documentation.

