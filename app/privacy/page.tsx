'use client';
import { AnimatedGradientBackground } from '@/components/AnimatedGradientBackground';
import { ScrollReveal } from '@/components/ScrollReveal';
import Link from 'next/link';

export default function PrivacyPage() {
  return (
    <>
      <AnimatedGradientBackground />
      <div className="relative z-10 pt-28 pb-20 px-4 md:px-8">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-12">
              <h1 className="text-5xl md:text-6xl font-serif mb-3">Privacy Policy</h1>
              <p className="text-cyan-400 text-sm uppercase tracking-wider">Last updated: June 2025</p>
            </div>
          </ScrollReveal>
          <ScrollReveal>
            <div className="glass-card rounded-3xl p-8 md:p-12 space-y-6 text-gray-300">
              <p>At Kalki Technologies, your privacy is our foundation. We do not collect, store, or share any personal data from your use of our AI services. All conversations with KI Bot run locally in your browser – no data ever leaves your device.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">Information We Collect</h2>
              <p>We collect only anonymous technical data necessary for the operation of our distributed node network: node ID (randomly generated), browser type, CPU cores, and memory (device memory API). This data is never linked to your identity and is automatically deleted after 1 hour.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">Use of Cookies</h2>
              <p>We use essential cookies only for localStorage of your conversation history and user preferences. No tracking cookies are used. You can clear localStorage at any time.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">Third‑Party Services</h2>
              <p>We use Supabase (for community posts) and Upstash Redis (for node counting). These services store only anonymised data as described above. No personal information is shared.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">Your Rights</h2>
              <p>Since we store no personal data, there is no data to access, correct, or delete. If you have questions, contact us at <a href="mailto:privacy@kalki.tech" className="text-cyan-400 hover:underline">privacy@kalki.tech</a>.</p>
              <div className="border-t border-white/10 pt-6 mt-6 text-sm text-gray-400">
                <p>Kalki Technologies – Open‑source intelligence engine. Registered MSME (Udyam).</p>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </>
  );
}
