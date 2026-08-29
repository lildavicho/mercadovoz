# Private real-data contract

`REAL_DEVELOPMENT` and `REAL_HELDOUT` are exported only to ignored/private storage. A record contains:

- `record_id`, `participant_id`, `session_id`;
- `original_text` and engine/pilot/schema versions;
- initial prediction and fields;
- final accepted fields and structured corrections;
- context and safety events;
- human outcome and relevant timestamps.

Participant IDs are pseudonyms. Identity mappings, access credentials, IP addresses and device fingerprints are excluded. `CONFIRMED` is labeled `USER_ACCEPTED_OPERATION`, not perfect ground truth.

The reproducible exporter is `scripts/export/export_real_development.py`. Do not place examples with real text in this document or in Git.
