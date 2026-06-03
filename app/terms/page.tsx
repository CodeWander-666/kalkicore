import { AnimatedGradientBackground } from '@/components/AnimatedGradientBackground';
import { ScrollReveal } from '@/components/ScrollReveal';
import Link from 'next/link';

export default function TermsPage() {
  return (
    <>
      <AnimatedGradientBackground />
      <div className="relative z-10 pt-28 pb-20 px-4 md:px-8">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-12">
              <h1 className="text-5xl md:text-6xl font-serif mb-3">Terms of Service</h1>
              <p className="text-cyan-400 text-sm uppercase tracking-wider">Effective: June 2025</p>
            </div>
          </ScrollReveal>
          <ScrollReveal>
            <div className="glass-card rounded-3xl p-8 md:p-12 space-y-6 text-gray-300">
              <p>Welcome to Kalki Technologies. By accessing our website or using our services (KI Bot, KI Cloud, community features), you agree to these Terms.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">1. Use of Services</h2>
              <p>Our services are provided "as is" for your personal or business use. You may not use our services for any illegal or harmful activity.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">2. User Content</h2>
              <p>You retain ownership of any content you submit to KI Community (posts, comments). You grant us a non‑exclusive license to display your content on our platform.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">3. Intellectual Property</h2>
              <p>All code, designs, and text on this site are open source under the MIT License unless otherwise stated. Our brand name and logo are trademarks of Kalki Technologies.</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">4. Limitation of Liability</h2>
              <p>We are not liable for any indirect or consequential damages arising from your use of our services. Our total liability shall not exceed the amount you paid us (if any).</p>
              <h2 className="text-2xl font-serif text-gold-400 mt-6">5. Changes to Terms</h2>
              <p>We may update these Terms at any time. Continued use of the site constitutes acceptance.</p>
              <div className="border-t border-white/10 pt-6 mt-6 text-sm text-gray-400">
                <p>Contact: <a href="mailto:legal@kalki.tech" className="text-cyan-400 hover:underline">legal@kalki.tech</a></p>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </>
  );
}
