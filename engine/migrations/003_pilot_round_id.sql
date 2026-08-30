ALTER TABLE pilot_sessions
ADD COLUMN round_id TEXT NOT NULL DEFAULT 'LEGACY_UNASSIGNED';

ALTER TABLE pilot_events
ADD COLUMN round_id TEXT NOT NULL DEFAULT 'LEGACY_UNASSIGNED';

UPDATE pilot_sessions
SET round_id = 'P01_R1'
WHERE participant_id = 'P01' AND engine_version = '1.0.0';

UPDATE pilot_events
SET round_id = COALESCE(
    (SELECT pilot_sessions.round_id FROM pilot_sessions WHERE pilot_sessions.id = pilot_events.session_id),
    'LEGACY_UNASSIGNED'
);

CREATE INDEX IF NOT EXISTS idx_sessions_round
ON pilot_sessions(participant_id, round_id, started_at);

CREATE INDEX IF NOT EXISTS idx_events_round
ON pilot_events(participant_id, round_id, occurred_at);
