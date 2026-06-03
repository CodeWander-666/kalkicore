'use client';
export const dynamic = 'force-dynamic';
import { Suspense, useState, useEffect, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { AnimatedGradientBackground } from '@/components/AnimatedGradientBackground';
import { ChatSidebar } from '@/components/chat/ChatSidebar';
import { WebLLMChat } from '@/components/WebLLMChat';
import { NodeTracker } from '@/components/NodeTracker';
import { Menu } from 'lucide-react';

interface Conversation {
  id: string;
  title: string;
  messages: any[];
  createdAt: number;
}

function ChatContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentId = searchParams.get('id');
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('ki_bot_conversations');
      if (stored) {
        const parsed = JSON.parse(stored);
        const validated = parsed.map((c: any) => ({ ...c, messages: Array.isArray(c.messages) ? c.messages : [] }));
        setConversations(validated);
      } else {
        const newId = crypto.randomUUID();
        const defaultConv = { id: newId, title: 'New Chat', messages: [], createdAt: Date.now() };
        setConversations([defaultConv]);
        localStorage.setItem('ki_bot_conversations', JSON.stringify([defaultConv]));
        router.push(`/ki-bot?id=${newId}`);
      }
    } catch (err) { console.error(err); }
  }, []);

  useEffect(() => {
    if (conversations.length && !currentId) router.push(`/ki-bot?id=${conversations[0].id}`);
  }, [conversations, currentId, router]);

  const saveConversations = (updated: Conversation[]) => {
    setConversations(updated);
    localStorage.setItem('ki_bot_conversations', JSON.stringify(updated));
  };

  const getCurrentConversation = () => {
    if (!currentId) return conversations[0];
    return conversations.find(c => c.id === currentId) || conversations[0];
  };

  const updateCurrentConversation = (updater: (conv: Conversation) => Conversation) => {
    const current = getCurrentConversation();
    if (!current) return;
    saveConversations(conversations.map(c => c.id === current.id ? updater(c) : c));
  };

  const addMessage = (message: any) => {
    updateCurrentConversation(conv => ({ ...conv, messages: [...(conv.messages || []), message] }));
    const current = getCurrentConversation();
    if ((current.messages?.length || 0) === 0 && message.role === 'user') {
      const newTitle = message.content.slice(0, 30) + (message.content.length > 30 ? '…' : '');
      updateCurrentConversation(conv => ({ ...conv, title: newTitle }));
    }
  };

  const newChat = () => {
    const newId = crypto.randomUUID();
    const newConv = { id: newId, title: 'New Chat', messages: [], createdAt: Date.now() };
    saveConversations([newConv, ...conversations]);
    router.push(`/ki-bot?id=${newId}`);
    setSidebarOpen(false);
  };

  const renameChat = (id: string, newTitle: string) => {
    saveConversations(conversations.map(c => c.id === id ? { ...c, title: newTitle } : c));
  };

  const deleteChat = (id: string) => {
    const updated = conversations.filter(c => c.id !== id);
    saveConversations(updated);
    if (id === currentId && updated.length > 0) router.push(`/ki-bot?id=${updated[0].id}`);
    else if (updated.length === 0) newChat();
  };

  const currentConv = getCurrentConversation();
  if (!currentConv) return null;

  return (
    <>
      <AnimatedGradientBackground />
      <div className="h-screen w-full fixed inset-0 flex flex-col bg-black/40">
        {/* Top bar */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10 bg-black/60 backdrop-blur-sm flex-shrink-0">
          <button onClick={() => setSidebarOpen(true)} className="p-1 rounded-lg hover:bg-white/10 md:hidden">
            <Menu size={22} className="text-white" />
          </button>
          <div className="flex-1" />
          <NodeTracker compact />
          <span className="text-gold-400 text-sm font-medium ml-2">KI Bot</span>
        </div>

        {/* Main area: takes remaining height */}
        <div className="flex-1 flex overflow-hidden min-h-0">
          <ChatSidebar
            conversations={conversations}
            currentId={currentId}
            onSelect={(id) => { router.push(`/ki-bot?id=${id}`); setSidebarOpen(false); }}
            onNew={newChat}
            onRename={renameChat}
            onDelete={deleteChat}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
          />

          {/* Chat container – also flex column to contain WebLLMChat's inner scroll */}
          <div className="flex-1 flex flex-col min-w-0 min-h-0 p-4">
            <div className={`flex-1 rounded-2xl transition-all duration-300 overflow-hidden ${isGenerating ? 'chat-glowing-border' : ''}`}>
              <WebLLMChat
                key={currentConv.id}
                messages={currentConv.messages}
                setMessages={(newMessages: any[]) => {
                  updateCurrentConversation(conv => ({ ...conv, messages: newMessages }));
                }}
                onNewMessage={addMessage}
                onGeneratingChange={setIsGenerating}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default function KIBotPage() {
  return (
    <Suspense fallback={<div className="h-screen flex items-center justify-center text-gold-400 bg-black">Loading chat...</div>}>
      <ChatContent />
    </Suspense>
  );
}
