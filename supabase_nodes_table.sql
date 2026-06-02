-- Run this SQL in your Supabase SQL Editor (https://supabase.com/dashboard/project/fbxsueskaqbwgwammgof/sql)
-- It adds the nodes table and cleanup function (idempotent)

CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY,
  device_name TEXT,
  cpu_cores INTEGER,
  memory REAL,
  benchmark INTEGER,
  last_seen BIGINT NOT NULL,
  created_at BIGINT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nodes_last_seen ON nodes(last_seen);
CREATE INDEX IF NOT EXISTS idx_nodes_id ON nodes(id);

-- Cleanup function: deletes nodes not seen in the last hour
CREATE OR REPLACE FUNCTION cleanup_old_nodes()
RETURNS void AS $$
BEGIN
  DELETE FROM nodes
  WHERE last_seen < (EXTRACT(EPOCH FROM NOW()) * 1000 - 3600000);
  RAISE NOTICE 'Deleted stale nodes (older than 1 hour)';
END;
$$ LANGUAGE plpgsql;

-- Optional: schedule cleanup every 30 minutes (requires pg_cron, skip if not available)
-- SELECT cron.schedule('cleanup_nodes', '*/30 * * * *', 'SELECT cleanup_old_nodes();');
