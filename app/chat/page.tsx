'use client';
export const dynamic = 'force-dynamic';
import { Suspense, useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { useKI } from '@/context/KIContext';
import { NodeTracker } from '@/components/NodeTracker';
import { GradientBackground } from '@/components/GradientBackground';
import Link from 'next/link';
import { Menu, X, Plus, Trash2, Edit2 } from 'lucide-react';

interface Conversation {
  id: string;
  title: string;
  messages: { role: 'user' | 'assistant'; content: string }[];
  createdAt: Date;
  updatedAt: Date;
}

function ChatContent() {
  const searchParams = useSearchParams();
  const currentId = searchParams.get('id');
  const { engine } = useKI();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  // Load/save conversations from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('ki_conversations');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        const convs = parsed.map((c: any) => ({
          ...c,
          messages: c.messages || [],
          createdAt: new Date(c.createdAt),
          updatedAt: new Date(c.updatedAt)
        }));
        setConversations(convs);
      } catch (e) {
        initDefaultConversation();
      }
    } else {
      initDefaultConversation();
    }
  }, []);

  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('ki_conversations', JSON.stringify(conversations));
    }
  }, [conversations]);

  const initDefaultConversation = () => {
    const newConv: Conversation = {
      id: crypto.randomUUID(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setConversations([newConv]);
    localStorage.setItem('ki_conversations', JSON.stringify([newConv]));
  };

  const getCurrentConversation = (): Conversation | undefined => {
    if (!currentId) return conversations[0];
    return conversations.find(c => c.id === currentId) || conversations[0];
  };

  const updateConversation = (id: string, updates: Partial<Conversation>) => {
    setConversations(prev => prev.map(c => c.id === id ? { ...c, ...updates, updatedAt: new Date() } : c));
  };

  const addMessage = (id: string, message: { role: 'user' | 'assistant'; content: string }) => {
    setConversations(prev => prev.map(c => {
      if (c.id !== id) return c;
      const messages = c.messages || [];
      return { ...c, messages: [...messages, message], updatedAt: new Date() };
    }));
  };

  const newChat = () => {
    const newConv: Conversation = {
      id: crypto.randomUUID(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setConversations(prev => [newConv, ...prev]);
    window.history.pushState({}, '', `/chat?id=${newConv.id}`);
    setDrawerOpen(false);
  };

  const renameChat = (id: string, newTitle: string) => {
    if (newTitle.trim()) {
      updateConversation(id, { title: newTitle.trim() });
    }
    setEditingId(null);
  };

  const deleteChat = (id: string) => {
    if (confirm('Delete this conversation permanently?')) {
      const newConversations = conversations.filter(c => c.id !== id);
      setConversations(newConversations);
      if (newConversations.length === 0) {
        initDefaultConversation();
      }
      if (currentId === id && newConversations.length > 0) {
        window.history.pushState({}, '', `/chat?id=${newConversations[0].id}`);
      }
    }
    setDrawerOpen(false);
  };

  const handleSendMessage = async (prompt: string): Promise<string> => {
    if (!engine) return 'Engine not ready';
    const currentConv = getCurrentConversation();
    if (!currentConv) return 'No conversation found';
    try {
      const trainingPrompt = `You are KI, the official AI assistant of Kalki Technologies.
Answer questions about web development, digital marketing, AI automation, SEO, social media, pricing, and company info. Be concise, friendly, and use markdown.`;
      const response = await engine.chat.completions.create({
        messages: [
          { role: 'system', content: trainingPrompt },
          ...(currentConv.messages || []),
          { role: 'user', content: prompt }
        ],
        max_tokens: 512,
        stream: false,
      });
      return response.choices[0].message.content;
    } catch (err) {
      console.error(err);
      return 'Sorry, I encountered an error. Please try again.';
    }
  };

  const currentConv = getCurrentConversation();
  if (!currentConv) return null;

  return (
    <>
      <GradientBackground />
      <div className="fixed inset-0 flex flex-col bg-black z-50">
        {/* Top bar – mobile first */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-black/60 backdrop-blur-sm">
          <button onClick={() => setDrawerOpen(true)} className="text-white p-1">
            <Menu size={24} />
          </button>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gold-400">KI</span>
            <NodeTracker compact />
          </div>
          <Link href="/" className="text-gray-400 text-xs">Exit</Link>
        </div>

        {/* Drawer (slide-out menu) */}
        <div className={`fixed inset-y-0 left-0 z-50 w-80 bg-black/95 backdrop-blur-xl border-r border-white/10 transform transition-transform duration-300 ease-out ${drawerOpen ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="flex flex-col h-full">
            <div className="flex justify-between items-center p-4 border-b border-white/10">
              <h2 className="text-gold-400 font-semibold">Conversations</h2>
              <button onClick={() => setDrawerOpen(false)} className="text-white p-1">
                <X size={20} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {conversations.map(conv => (
                <div key={conv.id} className="group relative">
                  {editingId === conv.id ? (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={e => setEditTitle(e.target.value)}
                      onBlur={() => renameChat(conv.id, editTitle)}
                      onKeyDown={e => e.key === 'Enter' && renameChat(conv.id, editTitle)}
                      className="w-full px-3 py-2 rounded-lg bg-white/10 text-sm focus:outline-none focus:ring-1 focus:ring-gold-400"
                      autoFocus
                    />
                  ) : (
                    <Link
                      href={`/chat?id=${conv.id}`}
                      onClick={() => setDrawerOpen(false)}
                      className={`block px-3 py-2 rounded-lg text-sm truncate ${currentConv?.id === conv.id ? 'bg-gold-500/20 text-gold-400' : 'text-gray-300 hover:bg-white/5'}`}
                    >
                      {conv.title}
                    </Link>
                  )}
                  <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1 opacity-0 group-hover:opacity-100 transition">
                    <button
                      onClick={() => { setEditingId(conv.id); setEditTitle(conv.title); }}
                      className="p-1 text-gray-400 hover:text-white"
                    >
                      <Edit2 size={14} />
                    </button>
                    <button
                      onClick={() => deleteChat(conv.id)}
                      className="p-1 text-gray-400 hover:text-red-400"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-4 border-t border-white/10">
              <button
                onClick={newChat}
                className="w-full py-2 rounded-full bg-gradient-to-r from-cyan-600 to-gold-600 text-white font-semibold flex items-center justify-center gap-2 hover:scale-105 transition"
              >
                <Plus size={18} /> New Chat
              </button>
            </div>
          </div>
        </div>

        {/* Chat area */}
        <div className="flex-1 overflow-hidden">
          <ChatInterface
            conversationId={currentConv.id}
            messages={currentConv.messages || []}
            onSendMessage={handleSendMessage}
            onNewMessage={(msg) => {
              addMessage(currentConv.id, msg);
              if ((currentConv.messages?.length || 0) === 0 && msg.role === 'user') {
                const newTitle = msg.content.slice(0, 30) + (msg.content.length > 30 ? '…' : '');
                updateConversation(currentConv.id, { title: newTitle });
              }
            }}
          />
        </div>
      </div>
    </>
  );
}

export default function ChatPage() {
  useEffect(() => {
    document.body.classList.add('chat-page');
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.classList.remove('chat-page');
      document.body.style.overflow = '';
    };
  }, []);

  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-gold-400 bg-black">Loading...</div>}>
      <ChatContent />
    </Suspense>
  );
}
