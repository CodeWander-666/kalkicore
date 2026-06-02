'use client';
import { useState } from 'react';
import { ScrollReveal } from '../../components/ScrollReveal';
import { NodeTracker } from '../../components/NodeTracker';
import { CommunityChat } from '@/components/ki-cloud/CommunityChat';
import { Marketplace } from '@/components/ki-cloud/Marketplace';
import { SocialFeed } from '@/components/ki-cloud/SocialFeed';
import { GradientBackground } from '@/components/GradientBackground';

type Tab = 'community' | 'marketplace' | 'bots' | 'social';

export default function KICloudPage() {
  const [activeTab, setActiveTab] = useState<Tab>('community');

  return (
    <>
      <GradientBackground />
      <div className="relative z-10 pt-24 pb-16 px-4 md:px-8 min-h-screen">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-gold-400/30 bg-gold-400/5 text-gold-400 text-sm tracking-wider mb-6">
              ✦ KI CLOUD – OPEN SOURCE ECOSYSTEM ✦
            </div>
            <h1 className="text-5xl md:text-7xl font-serif mb-4">
              Build. Share. <span className="text-gold-400">Earn.</span>
            </h1>
            <p className="text-gray-400 max-w-2xl mx-auto">
              The first cloud where developers grow together – communities, marketplaces, and social tools, all open source.
            </p>
            <div className="flex justify-center mt-6">
              <NodeTracker />
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-8">
            {/* Right Sidebar Menu */}
            <div className="md:w-72 order-1 md:order-2">
              <div className="glass-card rounded-2xl p-4 sticky top-28">
                <h3 className="text-lg font-semibold mb-4 text-gold-400">KI Cloud</h3>
                <nav className="space-y-2">
                  <button
                    onClick={() => setActiveTab('community')}
                    className={`w-full text-left px-4 py-2 rounded-lg transition ${
                      activeTab === 'community' ? 'bg-cyan-500/20 text-cyan-400 border-l-2 border-cyan-400' : 'hover:bg-white/5'
                    }`}
                  >
                    💬 KI Community Chat
                  </button>
                  <button
                    onClick={() => setActiveTab('marketplace')}
                    className={`w-full text-left px-4 py-2 rounded-lg transition ${
                      activeTab === 'marketplace' ? 'bg-cyan-500/20 text-cyan-400 border-l-2 border-cyan-400' : 'hover:bg-white/5'
                    }`}
                  >
                    🛒 KI Marketplace
                  </button>
                  <button
                    onClick={() => setActiveTab('bots')}
                    className={`w-full text-left px-4 py-2 rounded-lg transition ${
                      activeTab === 'bots' ? 'bg-cyan-500/20 text-cyan-400 border-l-2 border-cyan-400' : 'hover:bg-white/5'
                    }`}
                  >
                    🤖 KI Bots (Coming Soon)
                  </button>
                  <button
                    onClick={() => setActiveTab('social')}
                    className={`w-full text-left px-4 py-2 rounded-lg transition ${
                      activeTab === 'social' ? 'bg-cyan-500/20 text-cyan-400 border-l-2 border-cyan-400' : 'hover:bg-white/5'
                    }`}
                  >
                    📸 KI Social
                  </button>
                </nav>
              </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 order-2 md:order-1">
              <div className="glass-card rounded-3xl p-6 min-h-[600px]">
                {activeTab === 'community' && <CommunityChat />}
                {activeTab === 'marketplace' && <Marketplace />}
                {activeTab === 'bots' && (
                  <div className="text-center py-20 text-gray-400">
                    <div className="text-6xl mb-4">🤖</div>
                    <h3 className="text-2xl font-serif mb-2">KI Bots</h3>
                    <p>Coming soon – submit your own AI bots and earn KI credits.</p>
                  </div>
                )}
                {activeTab === 'social' && <SocialFeed />}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
