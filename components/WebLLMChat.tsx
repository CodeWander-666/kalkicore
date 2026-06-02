'use client';
import { useState, useRef, useEffect, useCallback } from 'react';
import { useKI } from '@/context/KIContext';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const getTrainingPrompt = () => `You are KI, the official AI assistant of Kalki Technologies.
COMPANY: Kalki Technologies (Kalkicore) – open‑source private AI.
SERVICES:
- Static Website: ₹7,999 one‑time (5 pages, responsive, SEO)
- Dynamic Next.js: ₹12,999 one‑time (15 pages, admin dashboard)
- GMB SEO: ₹8,999/month (Google Maps #1 ranking)
- Social Media Automation: ₹9,999/month (2 viral posts + blue tick)
- SEO Dominant: ₹9,999/month (50+ keywords, programmatic SEO)
- LinkedIn Optimisation: ₹9,999/month (free LinkedIn Premium)
CONTACT: WhatsApp +91 6261031710, email hello@kalki.tech
Be concise, helpful, privacy‑focused. Use markdown.`;

export function WebLLMChat({ 
  onGeneratingChange, 
  onNewMessage,
  messages: externalMessages,
  setMessages: externalSetMessages,
}: any) {
  const { engine, loading, activeNodes } = useKI();
  const [internalMessages, setInternalMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const messages = (externalMessages && Array.isArray(externalMessages)) ? externalMessages : internalMessages;
  const setMessages = useCallback((updater: any) => {
    if (externalSetMessages) {
      if (typeof updater === 'function') {
        const newMessages = updater(messages);
        if (Array.isArray(newMessages)) externalSetMessages(newMessages);
      } else if (Array.isArray(updater)) {
        externalSetMessages(updater);
      }
    } else {
      if (typeof updater === 'function') {
        setInternalMessages(prev => {
          const next = updater(prev);
          return Array.isArray(next) ? next : [];
        });
      } else if (Array.isArray(updater)) {
        setInternalMessages(updater);
      }
    }
  }, [externalSetMessages, messages]);

  useEffect(() => {
    if (onGeneratingChange) onGeneratingChange(isGenerating);
  }, [isGenerating, onGeneratingChange]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!engine || !input.trim() || isGenerating) return;
    const userMsg = { role: 'user', content: input };
    setMessages((prev: any[]) => [...(prev || []), userMsg]);
    if (onNewMessage) onNewMessage(userMsg);
    setInput('');
    setIsGenerating(true);
    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    try {
      const conversation = [
        { role: 'system', content: getTrainingPrompt() },
        ...(messages || []),
        userMsg,
      ];
      const stream = await engine.chat.completions.create({
        messages: conversation,
        stream: true,
        max_tokens: 512,
      });
      let full = '';
      for await (const chunk of stream) {
        const delta = chunk.choices[0]?.delta?.content;
        if (delta) full += delta;
        setMessages((prev: any[]) => {
          const last = prev[prev.length - 1];
          if (last?.role === 'assistant') {
            const updated = [...prev];
            updated[updated.length - 1] = { ...last, content: full };
            return updated;
          } else {
            return [...prev, { role: 'assistant', content: full }];
          }
        });
      }
      if (onNewMessage) onNewMessage({ role: 'assistant', content: full });
    } catch (err) {
      console.error(err);
      setMessages((prev: any[]) => [...prev, { role: 'assistant', content: 'Sorry, an error occurred.' }]);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const autoResize = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const target = e.target;
    target.style.height = 'auto';
    target.style.height = Math.min(target.scrollHeight, 200) + 'px';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gold-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gold-400">Loading KI engine...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-black/30 rounded-2xl overflow-hidden">
      {/* Scrollable messages area - takes all available space */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 py-12">
            <p className="text-4xl mb-2">🤖</p>
            <p>Ask KI anything – private, local AI.</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-2xl ${msg.role === 'user' ? 'bg-gold-600/20 border border-gold-400/30' : 'glass-card border border-white/10'}`}>
              {msg.role === 'assistant' ? (
                <ReactMarkdown
                  components={{
                    code({ node, inline, className, children, ...props }: any) {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="div" {...props}>
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>{children}</code>
                      );
                    },
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              ) : (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              )}
            </div>
          </div>
        ))}
        {isGenerating && (
          <div className="flex justify-start">
            <div className="glass-card p-3 rounded-2xl">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gold-400 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-gold-400 rounded-full animate-bounce delay-150" />
                <span className="w-2 h-2 bg-gold-400 rounded-full animate-bounce delay-300" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Fixed input area - never scrolls */}
      <div className="p-4 border-t border-white/10 bg-black/20 flex-shrink-0">
        <div className="flex gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => { setInput(e.target.value); autoResize(e); }}
            onKeyDown={handleKeyDown}
            placeholder="Ask KI anything..."
            rows={1}
            className="flex-1 bg-black/50 rounded-2xl px-4 py-3 border border-gold-400/30 focus:outline-none focus:border-gold-400 resize-none overflow-y-auto max-h-32"
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isGenerating}
            className="px-5 py-3 rounded-full bg-gold-600 text-white font-semibold disabled:opacity-50 hover:scale-105 transition"
          >
            Send
          </button>
        </div>
        <p className="text-[10px] text-gray-500 text-center mt-2">
          🔒 {activeNodes} active nodes · private · local AI
        </p>
      </div>
    </div>
  );
}
