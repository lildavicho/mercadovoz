# Security policy

## Supported branch

Security fixes are supported on `main`. During active development they must also be merged back into `develop`.

## Reporting

Use GitHub's private vulnerability reporting feature for this repository. Do not open a public issue containing credentials, private URLs, participant text, database contents or exploit details.

If private reporting is unavailable, open a minimal public issue asking the maintainer to enable a private channel; do not include the vulnerability details.

## Pilot data

Pilot data is private. Never commit participant identity mappings, `REAL_DEVELOPMENT`, `REAL_HELDOUT`, databases, backups, audio, logs with user text, access codes or operator tokens.

## Secrets

If a secret is exposed, revoke/rotate it before removing it from code or history. A deletion commit alone does not make a published secret safe.

This policy does not claim certification or regulatory compliance.
