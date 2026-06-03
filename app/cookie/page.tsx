import { AnimatedGradientBackground } from '@/components/AnimatedGradientBackground';
import { ScrollReveal } from '@/components/ScrollReveal';
import Link from 'next/link';

export default function CookiePage() {
  return (
    <>
      <AnimatedGradientBackground />
      <div className="relative z-10 pt-28 pb-20 px-4 md:px-8">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-12">
              <h1 className="text-5xl md:text-6xl font-serif mb-3">Cookie Policy</h1>
              <p className="text-cyan-400 text-sm uppercase tracking-wider">Last updated: June 2025</p>
            </div>
          </ScrollReveal>
          <ScrollReveal>
            <div className="glass-card rounded-3xl p-8 md:p-12 space-y-6 text-gray-300">
              <p>We use minimal, essential cookies only. No tracking, no analytics, no advertising cookies.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">What Are Cookies</h2>
              <p>Cookies are small text files stored on your device. We use localStorage (a modern alternative) to save your conversation history and site preferences.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">Cookies We Use</h2>
              <ul className="list-disc pl-5 space-y-1">
                <li><strong>ki_bot_conversations</strong> – stores your chat history (localStorage).</li>
                <li><strong>ki_conversations</strong> – stores your KI Cloud chat history (localStorage).</li>
                <li><strong>ki_node_id</strong> – a random ID for node counting (localStorage).</li>
              </ul>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">Your Control</h2>
              <p>You can clear localStorage at any time via browser settings. This will remove all conversation history but will not affect our service’s core functionality.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">No Third‑Party Cookies</h2>
              <p>We do not use Google Analytics, Facebook Pixel, or any tracking scripts. Your privacy is absolute.</p>
              <div className="border-t border-white/10 pt-6 mt-6 text-sm text-gray-400">
                <p>Questions? <a href="mailto:privacy@kalki.tech" className="text-cyan-400 hover:underline">privacy@kalki.tech</a></p>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </>
  );
}
