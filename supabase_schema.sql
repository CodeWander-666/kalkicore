-- Run this SQL in your Supabase SQL Editor (https://supabase.com/dashboard/project/fbxsueskaqbwgwammgof/sql)
-- It will create all necessary tables and the "kalkicore" community.

-- Communities table
CREATE TABLE IF NOT EXISTS communities (
  id TEXT PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  created_at BIGINT NOT NULL
);

-- Posts table
CREATE TABLE IF NOT EXISTS posts (
  id TEXT PRIMARY KEY,
  community_id TEXT NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
  author TEXT NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  upvotes INTEGER DEFAULT 0,
  downvotes INTEGER DEFAULT 0,
  created_at BIGINT NOT NULL
);

-- Comments table
CREATE TABLE IF NOT EXISTS comments (
  id TEXT PRIMARY KEY,
  post_id TEXT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  author TEXT NOT NULL,
  content TEXT NOT NULL,
  upvotes INTEGER DEFAULT 0,
  downvotes INTEGER DEFAULT 0,
  created_at BIGINT NOT NULL
);

-- Enable Row Level Security
ALTER TABLE communities ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;

-- Public read/write policies (no login required)
CREATE POLICY "Public read communities" ON communities FOR SELECT USING (true);
CREATE POLICY "Public insert communities" ON communities FOR INSERT WITH CHECK (true);

CREATE POLICY "Public read posts" ON posts FOR SELECT USING (true);
CREATE POLICY "Public insert posts" ON posts FOR INSERT WITH CHECK (true);

CREATE POLICY "Public read comments" ON comments FOR SELECT USING (true);
CREATE POLICY "Public insert comments" ON comments FOR INSERT WITH CHECK (true);

-- Seed the "kalkicore" community
INSERT INTO communities (id, name, description, created_at)
VALUES ('kalkicore', 'kalkicore', 'Official community for Kalki Intelligency – discuss private AI, digital marketing, web dev, and KI Cloud.', EXTRACT(EPOCH FROM NOW()) * 1000)
ON CONFLICT (name) DO NOTHING;
