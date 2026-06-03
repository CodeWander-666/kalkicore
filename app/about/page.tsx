import { AnimatedGradientBackground } from '../../components/AnimatedGradientBackground';
import { ScrollReveal } from '../../components/ScrollReveal';
import Link from 'next/link';

export default function AboutPage() {
  return (
    <>
      <AnimatedGradientBackground />
      <div className="relative z-10 pt-28 pb-20 px-4 md:px-8">
        <div className="max-w-7xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-gold-400/30 bg-gold-400/5 text-gold-400 text-sm tracking-wider mb-6 backdrop-blur-sm">
                ✦ ABOUT KALKI TECHNOLOGIES ✦
              </div>
              <h1 className="text-6xl md:text-8xl font-serif mb-6">
                The <span className="text-gold-400">Intelligence</span> Behind the Engine
              </h1>
              <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                Registered MSME (Udyam) dedicated to building open‑source, private AI for everyone.
              </p>
            </div>
          </ScrollReveal>

          <ScrollReveal>
            <div className="grid md:grid-cols-2 gap-8 mb-24">
              <div className="glass-card p-10 rounded-2xl border-l-4 border-gold-400">
                <h2 className="text-3xl font-serif mb-4">Our <span className="text-gold-400">Mission</span></h2>
                <p className="text-gray-300 leading-relaxed">
                  Democratise artificial intelligence by making it accessible, affordable, and completely private.
                  We believe that the most powerful technology of our time should not be locked behind corporate walls or paywalls.
                  Every line of our code is open source – transparent, auditable, and free.
                </p>
              </div>
              <div className="glass-card p-10 rounded-2xl border-l-4 border-cyan-400">
                <h2 className="text-3xl font-serif mb-4">Our <span className="text-cyan-400">Vision</span></h2>
                <p className="text-gray-300 leading-relaxed">
                  Build the world's first truly distributed intelligence network – where every device contributes,
                  every user owns their data, and AI serves humanity, not the other way around.
                </p>
              </div>
            </div>
          </ScrollReveal>

          <ScrollReveal>
            <div className="glass-card rounded-3xl p-12 mb-24">
              <h2 className="text-4xl font-serif mb-8">Our <span className="text-gold-400">Story</span></h2>
              <p className="text-gray-300 leading-relaxed text-lg mb-6">
                Kalki Technologies was founded with a single belief: artificial intelligence should be accessible,
                transparent, and owned by the people. In a world where AI is increasingly locked behind corporate walls,
                we set out to build an alternative – an open‑source intelligence engine that runs entirely on your device,
                respects your privacy, and gets smarter with every node.
              </p>
              <p className="text-gray-300 leading-relaxed text-lg">
                Today, we are a registered MSME (Udyam), serving 50+ businesses across India and beyond.
                Our platform – KI Cloud – combines WebLLM technology, quantum‑inspired parallel processing,
                and a distributed node network to deliver AI that is both powerful and private.
              </p>
            </div>
          </ScrollReveal>

          <div className="grid md:grid-cols-3 gap-8 mb-24">
            <ScrollReveal>
              <div className="glass-card p-8 text-center rounded-2xl">
                <div className="text-6xl mb-4">🔓</div>
                <h3 className="text-xl font-semibold mb-2">Open Source</h3>
                <p className="text-gray-400 text-sm">Every line of code is transparent. No black boxes, no hidden agendas.</p>
              </div>
            </ScrollReveal>
            <ScrollReveal>
              <div className="glass-card p-8 text-center rounded-2xl">
                <div className="text-6xl mb-4">🔒</div>
                <h3 className="text-xl font-semibold mb-2">Privacy First</h3>
                <p className="text-gray-400 text-sm">Your data never leaves your device. We don't store, we don't sell.</p>
              </div>
            </ScrollReveal>
            <ScrollReveal>
              <div className="glass-card p-8 text-center rounded-2xl">
                <div className="text-6xl mb-4">🤝</div>
                <h3 className="text-xl font-semibold mb-2">Community Driven</h3>
                <p className="text-gray-400 text-sm">Every node contributes to the network. We grow together.</p>
              </div>
            </ScrollReveal>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-24">
            {[
              { num: '50+', label: 'Active Clients' },
              { num: '10K+', label: 'Leads Generated' },
              { num: '100%', label: 'Open Source' },
              { num: '24/7', label: 'AI Support' },
            ].map((stat, idx) => (
              <ScrollReveal key={idx}>
                <div className="glass-card p-6 text-center rounded-2xl">
                  <div className="text-4xl font-serif text-gold-400 mb-2">{stat.num}</div>
                  <div className="text-gray-400 text-sm">{stat.label}</div>
                </div>
              </ScrollReveal>
            ))}
          </div>

          <ScrollReveal>
            <div className="text-center">
              <Link
                href="/contact"
                className="inline-block px-10 py-4 rounded-full bg-gradient-to-r from-gold-600 to-cyan-600 text-white font-semibold hover:scale-105 transition"
              >
                Become a Partner →
              </Link>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </>
  );
}
