# Runtime data

Runtime data lives outside source control.

Expected deployment path:

```text
/home/ubuntu/apps/mercadovoz/data/runtime/
  mercadovoz-pilot.db
  mercadovoz-pilot.db-wal
  mercadovoz-pilot.db-shm
```

This directory may also hold private exports temporarily, but those files must be moved to controlled encrypted storage and deleted according to the pilot retention policy. Git ignores `data/runtime/` and `data/private/`.

Never place participant identity mappings, `REAL_DEVELOPMENT`, `REAL_HELDOUT`, audio, backups or operational logs in a versioned directory. Synthetic/public benchmark inputs belong under `research/`, not here.
