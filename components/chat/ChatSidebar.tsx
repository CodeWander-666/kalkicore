'use client';
import { useState } from 'react';

interface Conversation {
  id: string;
  title: string;
  messages: any[];
  createdAt: number;
}

export function ChatSidebar({ conversations, currentId, onSelect, onNew, onRename, onDelete, isOpen, onClose }: any) {
  const [menuOpen, setMenuOpen] = useState<string | null>(null);

  return (
    <>
      {isOpen && <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={onClose} />}
      <div className={`fixed top-0 left-0 bottom-0 w-80 bg-black/90 backdrop-blur-xl border-r border-white/10 z-50 transform transition-transform duration-300 flex flex-col ${isOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0`}>
        <div className="p-4 border-b border-white/10 flex justify-between items-center flex-shrink-0">
          <h2 className="text-gold-400 font-semibold">Conversations</h2>
          <button onClick={onNew} className="p-1 rounded-lg hover:bg-white/10 text-white">+</button>
          <button className="md:hidden p-1" onClick={onClose}>✕</button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.map((conv: Conversation) => (
            <div key={conv.id} className={`group relative flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer ${currentId === conv.id ? 'bg-white/10 text-gold-400' : 'text-gray-300 hover:bg-white/5'}`} onClick={() => onSelect(conv.id)}>
              <span className="truncate text-sm flex-1">{conv.title}</span>
              <button onClick={(e) => { e.stopPropagation(); setMenuOpen(menuOpen === conv.id ? null : conv.id); }} className="opacity-0 group-hover:opacity-100 p-1">⋮</button>
              {menuOpen === conv.id && (
                <div className="absolute right-0 top-full mt-1 bg-black/90 rounded-lg shadow-lg border border-white/10 z-20 min-w-[100px]">
                  <button onClick={() => { const newTitle = prompt('New title:', conv.title); if (newTitle) onRename(conv.id, newTitle); setMenuOpen(null); }} className="block w-full text-left px-3 py-2 text-sm">✏️ Rename</button>
                  <button onClick={() => { if (confirm('Delete?')) onDelete(conv.id); setMenuOpen(null); }} className="block w-full text-left px-3 py-2 text-sm text-red-400">🗑️ Delete</button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
