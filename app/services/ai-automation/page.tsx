import VideoSchema from './video-schema';
import { AnimatedGradientBackground } from '@/components/AnimatedGradientBackground';
import { ScrollReveal } from '@/components/ScrollReveal';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function AIAutomationPage() {
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
              <h1 className="text-5xl md:text-6xl font-serif mb-3">AI Automation Suite</h1>
              <p className="text-cyan-400 text-sm uppercase tracking-wider">WhatsApp bots, booking dashboards, AI sales agents – guaranteed ROI</p>
      <VideoSchema />
            </div>
          </ScrollReveal>
          <ScrollReveal>
            <div className="glass-card rounded-3xl p-4 mb-12">
              <video src="/videos/ai-automation.webm" autoPlay loop muted playsInline className="w-full rounded-2xl border border-gold-400/30" />
      <VideoSchema />
            </div>
          </ScrollReveal>
          <ScrollReveal>
            <div className="glass-card rounded-3xl p-8 md:p-12 mb-8">
              <p className="text-gray-300 leading-relaxed">Custom AI agents for sales, support, and internal processes – all powered by your private KI instance. Your data never leaves your infrastructure.</p>
              <ul className="space-y-3 mt-6">
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">WhatsApp chatbot for lead qualification</span></li>
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">Email drip campaigns with AI copy</span></li>
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">AI calling agent for appointment setting</span></li>
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">Retargeting ads with predictive LTV models</span></li>
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">Full CRM integration (HubSpot, Salesforce, Pipedrive)</span></li>
                <li className="flex items-start gap-3"><span className="text-gold-400">✦</span> <span className="text-gray-300">Custom workflow automation (Zapier alternative)</span></li>
              </ul>
              <div className="bg-cyan-400/10 p-5 rounded-xl mt-8 border-l-4 border-cyan-400">
                <p className="text-sm italic text-gray-300"><span className="font-bold text-cyan-400">Why we’re different:</span> Our AI runs entirely on your infrastructure – zero data leakage, total control. We build, you own the intellectual property.</p>
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
