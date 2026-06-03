import VideoSchema from './video-schema';
import { AnimatedGradientBackground } from '@/components/AnimatedGradientBackground';
import { ScrollReveal } from '@/components/ScrollReveal';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function SEOPage() {
  return (
    <>
      <AnimatedGradientBackground />
      <div className="relative z-10 pt-28 pb-20 px-4 md:px-8 min-h-screen">
        <div className="max-w-5xl mx-auto">
          <Link href="/services" className="inline-flex items-center gap-1 text-gold-400 text-sm mb-6 hover:underline">
            <ArrowLeft className="w-4 h-4" /> Back to all services
          </Link>
          <ScrollReveal>
            <div className="text-center mb-12">
              <h1 className="text-5xl md:text-6xl font-serif mb-3">AI‑Driven SEO</h1>
              <p className="text-cyan-400 text-sm uppercase tracking-wider">Programmatic SEO, on‑page & off‑page optimisation, local dominance</p>
      <VideoSchema />
            </div>
          </ScrollReveal>
          <ScrollReveal>
            <div className="glass-card rounded-3xl p-4 mb-12">
              <video src="/videos/ai-seo.webm" autoPlay loop muted playsInline className="w-full rounded-2xl border border-gold-400/30" />
      <VideoSchema />
            </div>
          </ScrollReveal>
          <ScrollReveal>
            <div className="glass-card rounded-3xl p-8 md:p-12 mb-8">
              <p className="text-gray-300 leading-relaxed">Rank #1 on Google with our AI‑powered SEO suite. We combine programmatic landing pages, technical audits, and backlink strategies that actually work.</p>
              <ul className="space-y-3 mt-6">
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">50+ high‑intent keywords targeted monthly</span></li>
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">Programmatic AI landing pages at scale</span></li>
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">Technical SEO audit & Core Web Vitals fix</span></li>
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">Competitor gap analysis & backlink acquisition</span></li>
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">Monthly white‑label reports with ROI tracking</span></li>
              </ul>
              <div className="bg-cyan-400/10 p-5 rounded-xl mt-8 border-l-4 border-cyan-400">
                <p className="text-sm italic text-gray-300"><span className="font-bold text-cyan-400">Why we’re different:</span> We combine open‑source AI (KI) with human expertise – you see every change, no black‑box tricks.</p>
      <VideoSchema />
              </div>
              <div className="flex flex-wrap gap-4 mt-8">
                <Link href="/contact" className="px-8 py-3 rounded-full bg-gradient-to-r from-gold-600 to-cyan-600 text-white font-semibold hover:scale-105 transition">Get a Free Consultation →</Link>
                <Link href="/support" className="px-8 py-3 rounded-full border border-white/20 text-white hover:border-gold-400 transition">Chat with Support</Link>
      <VideoSchema />
              </div>
      <VideoSchema />
            </div>
          </ScrollReveal>
      <VideoSchema />
        </div>
      <VideoSchema />
      </div>
    </>
  );
}
