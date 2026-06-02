'use client';
import { AnimatedGradientBackground } from '@/components/AnimatedGradientBackground';
import { ScrollReveal } from '@/components/ScrollReveal';
import Link from 'next/link';

export default function GDPRPage() {
  return (
    <>
      <AnimatedGradientBackground />
      <div className="relative z-10 pt-28 pb-20 px-4 md:px-8">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-12">
              <h1 className="text-5xl md:text-6xl font-serif mb-3">GDPR Compliance</h1>
              <p className="text-cyan-400 text-sm uppercase tracking-wider">EU General Data Protection Regulation</p>
            </div>
          </ScrollReveal>
          <ScrollReveal>
            <div className="glass-card rounded-3xl p-8 md:p-12 space-y-6 text-gray-300">
              <p>Kalki Technologies fully complies with the GDPR. We are a data‑minimalist, privacy‑first service.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">Your Rights Under GDPR</h2>
              <ul className="list-disc pl-5 space-y-1">
                <li><strong>Right to access</strong> – we store no personal data, so there is nothing to access.</li>
                <li><strong>Right to rectification</strong> – not applicable as we hold no data.</li>
                <li><strong>Right to erasure</strong> – you can clear localStorage at any time.</li>
                <li><strong>Right to restrict processing</strong> – no processing occurs.</li>
                <li><strong>Right to data portability</strong> – you can export your chat history via browser dev tools.</li>
                <li><strong>Right to object</strong> – you may stop using our services at any time.</li>
              </ul>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">Data Protection Officer</h2>
              <p>Contact our DPO: <a href="mailto:dpo@kalki.tech" className="text-cyan-400 hover:underline">dpo@kalki.tech</a>. We respond within 30 days.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">International Transfers</h2>
              <p>Your data never leaves your browser. Our servers only process anonymous node metadata and community posts (no personal identification).</p>
              <div className="bg-cyan-400/10 p-4 rounded-xl border-l-4 border-cyan-400 mt-6">
                <p className="text-sm">✅ Kalki Technologies is GDPR‑compliant by design – no user tracking, no data collection, total privacy.</p>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </>
  );
}
