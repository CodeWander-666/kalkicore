-- Run this SQL in your Supabase SQL Editor to add the cleanup function
-- (if not already present from previous steps)

CREATE OR REPLACE FUNCTION cleanup_old_nodes()
RETURNS void AS $$
BEGIN
  DELETE FROM nodes
  WHERE last_seen < (EXTRACT(EPOCH FROM NOW()) * 1000 - 3600000);
  RAISE NOTICE 'Deleted stale nodes (older than 1 hour)';
END;
$$ LANGUAGE plpgsql;

-- Optional: run the function once to clean old data
SELECT cleanup_old_nodes();
