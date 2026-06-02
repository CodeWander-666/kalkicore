'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Footer() {
  const currentYear = new Date().getFullYear();
  const pathname = usePathname();
  // Hide footer on full‑screen pages (chat, ki-bot)
  if (pathname === '/chat' || pathname === '/ki-bot') return null;

  return (
    <footer className="relative z-20 border-t border-white/10 bg-black/80 backdrop-blur-xl mt-20">
      <div className="max-w-7xl mx-auto px-6 py-12 md:py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-gold-400 text-xl">⚡</span>
              <span className="text-xl font-serif bg-gradient-to-r from-cyan-400 via-gold-400 to-cyan-400 bg-clip-text text-transparent">KALKI</span>
            </div>
            <p className="text-gray-400 text-xs leading-relaxed">
              Open‑source intelligence engine. Private AI that runs in your browser. Registered MSME (Udyam).
            </p>
            <div className="flex gap-4 pt-2">
              <a href="https://github.com/CodeWander-666" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-gold-400 transition">GitHub</a>
              <a href="https://wa.me/916261031710" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-gold-400 transition">WhatsApp</a>
              <a href="mailto:hello@kalki.tech" className="text-gray-400 hover:text-gold-400 transition">Email</a>
            </div>
          </div>

          {/* Explore */}
          <div>
            <h3 className="text-gold-400 text-xs font-semibold uppercase tracking-wider mb-4">Explore</h3>
            <ul className="space-y-2">
              <li><Link href="/" className="text-gray-400 hover:text-gold-400 text-sm">Home</Link></li>
              <li><Link href="/ki-cloud" className="text-gray-400 hover:text-gold-400 text-sm">KI Cloud</Link></li>
              <li><Link href="/digital-marketing" className="text-gray-400 hover:text-gold-400 text-sm">Digital Marketing</Link></li>
              <li><Link href="/plans" className="text-gray-400 hover:text-gold-400 text-sm">Plans</Link></li>
              <li><Link href="/about" className="text-gray-400 hover:text-gold-400 text-sm">About</Link></li>
              <li><Link href="/vision" className="text-gray-400 hover:text-gold-400 text-sm">Vision</Link></li>
              <li><Link href="/hiring" className="text-gray-400 hover:text-gold-400 text-sm">Hiring</Link></li>
              <li><Link href="/support" className="text-gray-400 hover:text-gold-400 text-sm">Support</Link></li>
              <li><Link href="/ki-bot" className="text-gray-400 hover:text-gold-400 text-sm">KI Bot</Link></li>
            </ul>
          </div>

          {/* Services */}
          <div>
            <h3 className="text-gold-400 text-xs font-semibold uppercase tracking-wider mb-4">Services</h3>
            <ul className="space-y-2">
              <li><Link href="/services/seo" className="text-gray-400 hover:text-gold-400 text-sm">AI SEO</Link></li>
              <li><Link href="/services/social-media" className="text-gray-400 hover:text-gold-400 text-sm">Social Media</Link></li>
              <li><Link href="/services/gmb-seo" className="text-gray-400 hover:text-gold-400 text-sm">GMB SEO</Link></li>
              <li><Link href="/services/linkedin" className="text-gray-400 hover:text-gold-400 text-sm">LinkedIn Growth</Link></li>
              <li><Link href="/services/web-development" className="text-gray-400 hover:text-gold-400 text-sm">Web Development</Link></li>
              <li><Link href="/services/ai-automation" className="text-gray-400 hover:text-gold-400 text-sm">AI Automation</Link></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-gold-400 text-xs font-semibold uppercase tracking-wider mb-4">Legal</h3>
            <ul className="space-y-2 mb-6">
              <li><Link href="/privacy" className="text-gray-400 hover:text-gold-400 text-sm">Privacy Policy</Link></li>
              <li><Link href="/terms" className="text-gray-400 hover:text-gold-400 text-sm">Terms of Service</Link></li>
              <li><Link href="/cookie" className="text-gray-400 hover:text-gold-400 text-sm">Cookie Policy</Link></li>
              <li><Link href="/gdpr" className="text-gray-400 hover:text-gold-400 text-sm">GDPR Compliance</Link></li>
            </ul>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <span className="text-gold-400">✓</span> GDPR Compliant
            </div>
          </div>
        </div>

        <div className="border-t border-white/10 mt-10 pt-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-gray-500 text-[10px] uppercase tracking-wider">© {currentYear} Kalki Technologies. All rights reserved.</p>
          <div className="flex gap-6">
            <span className="text-[10px] text-gray-500 flex items-center gap-1">🌍 India</span>
            <span className="text-[10px] text-gray-500 flex items-center gap-1">📄 MSME Registered</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
