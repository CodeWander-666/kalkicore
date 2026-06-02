'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

interface Post {
  id: string;
  title: string;
  content: string;
  upvotes: number;
  downvotes: number;
  created_at: number;
  author: string;
}

export function CommunityChat() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch initial posts
    supabase
      .from('posts')
      .select('*')
      .order('created_at', { ascending: false })
      .then(({ data, error }) => {
        if (!error && data) setPosts(data);
        setLoading(false);
      });

    // Subscribe to new posts
    const subscription = supabase
      .channel('posts-channel')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'posts' }, (payload) => {
        setPosts(prev => [payload.new as Post, ...prev]);
      })
      .subscribe();

    return () => { subscription.unsubscribe(); };
  }, []);

  const createPost = async () => {
    if (!newTitle.trim() || !newContent.trim()) return;
    const newPost = {
      id: crypto.randomUUID(),
      title: newTitle,
      content: newContent,
      upvotes: 0,
      downvotes: 0,
      created_at: Date.now(),
      author: 'User',
      community_id: 'kalkicore',
    };
    await supabase.from('posts').insert(newPost);
    setNewTitle('');
    setNewContent('');
  };

  if (loading) return <div className="text-center py-10">Loading community...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-serif">KI Community (Reddit Style)</h2>
      <div className="glass-card p-4 rounded-xl space-y-3">
        <input
          type="text"
          placeholder="Post title"
          value={newTitle}
          onChange={e => setNewTitle(e.target.value)}
          className="w-full bg-black/50 rounded-lg px-3 py-2"
        />
        <textarea
          placeholder="Content"
          value={newContent}
          onChange={e => setNewContent(e.target.value)}
          rows={3}
          className="w-full bg-black/50 rounded-lg px-3 py-2"
        />
        <button onClick={createPost} className="bg-cyan-600 px-4 py-2 rounded-full text-sm">Create Post</button>
      </div>
      {posts.map(post => (
        <div key={post.id} className="glass-card p-4 rounded-xl">
          <h3 className="text-xl font-semibold">{post.title}</h3>
          <p className="text-gray-300 mt-1">{post.content}</p>
          <div className="flex gap-2 mt-2 text-xs text-gray-400">
            <span>👍 {post.upvotes}</span>
            <span>👎 {post.downvotes}</span>
            <span>💬 0</span>
          </div>
        </div>
      ))}
    </div>
  );
}
