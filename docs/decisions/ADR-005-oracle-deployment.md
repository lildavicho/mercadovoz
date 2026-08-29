# ADR-005 — Oracle Cloud single-instance deployment

**Status:** prepared, not deployed.

## Context

The private pilot needs an ARM64-capable, low-cost persistent host without introducing a managed database before concurrency justifies it.

## Decision

Prepare one Oracle Cloud `VM.Standard.A1.Flex` instance with Ubuntu 24.04 ARM64, 2 OCPU, 12 GB RAM and a 50 GB persistent boot volume. Nginx terminates HTTPS and proxies Next.js/PM2 plus FastAPI/systemd. SQLite WAL lives outside Git on the persistent volume.

## Consequences

This is a singleton: no horizontal replicas and a brief maintenance window for deploys. The operator owns OS patching, TLS, firewall, backup and restore drills. PostgreSQL becomes the next option if concurrency, multi-instance deployment or granular recovery becomes necessary.

The repository setup does not create the VM, networking, DNS or credentials.
