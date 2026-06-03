import { ScrollReveal } from '../../components/ScrollReveal';
import { AnimatedGradient } from '../../components/AnimatedGradient';
import Link from 'next/link';
import Image from 'next/image';

// Service data – each with video, bullet points, CTAs
const services = [
  {
    id: 'seo',
    title: 'SEO Optimization & Dominance',
    tagline: 'Rank #1 on Google – organically',
    video: '/videos/seo_optimization.webm',
    points: [
      '✅ 50+ high‑intent keywords targeted monthly',
      '✅ Programmatic SEO at scale (AI‑generated landing pages)',
      '✅ Technical SEO audit & fix (Core Web Vitals, schema markup)',
      '✅ Local SEO – Google Maps pack dominance',
      '✅ Monthly white‑label reports with ROI tracking',
      '✅ Competitor backlink analysis & acquisition'
    ],
    whyDifferent: 'We combine open‑source AI (KI) with human expertise – you see every change, no black‑box tricks.'
  },
  {
    id: 'social',
    title: 'Social Media Automation',
    tagline: 'Facebook + Instagram – go viral, guaranteed',
    video: '/videos/social_media_automation.webm',
    points: [
      '✅ 2 viral posts guaranteed per month (algorithm‑optimised)',
      '✅ Free blue tick verification on Instagram/Facebook',
      '✅ Daily automated content scheduling (AI‑generated posts)',
      '✅ Engagement boosting – real comments, shares, saves',
      '✅ Full analytics dashboard – track reach, clicks, conversions',
      '✅ Competitor social spying & trend hijacking'
    ],
    whyDifferent: 'Our KI engine predicts viral patterns before they trend – your brand becomes the trend.'
  },
  {
    id: 'gmb',
    title: 'Google Business Profile SEO',
    tagline: 'Own your local market',
    video: '/videos/gmb_seo.webm',
    points: [
      '✅ #1 ranking on Google Maps for your primary keywords',
      '✅ Review management – auto‑reply, sentiment analysis',
      '✅ Local citation building (100+ directories)',
      '✅ GBP post automation (events, offers, updates)',
      '✅ Q&A optimisation with AI‑generated answers',
      '✅ Insights dashboard – track calls, direction requests, website clicks'
    ],
    whyDifferent: 'We use distributed node network to test local ranking factors in real time – no other agency does this.'
  },
  {
    id: 'content',
    title: 'AI Content Marketing',
    tagline: 'Blog posts, articles, whitepapers that rank',
    video: '/videos/content_marketing.webm',
    points: [
      '✅ 4 SEO‑optimised articles per month (1,500+ words each)',
      '✅ AI humaniser – passes all AI detectors',
      '✅ Internal linking strategy to boost domain authority',
      '✅ Featured snippet optimisation',
      '✅ Content repurposing – turn blogs into social posts, newsletters',
      '✅ Competitor content gap analysis'
    ],
    whyDifferent: 'Our training data includes 10M+ high‑ranking articles – KI writes like a senior human expert.'
  },
  {
    id: 'linkedin',
    title: 'LinkedIn Growth Engine',
    tagline: 'B2B leads on autopilot',
    video: '/videos/linkedin_growth.webm',
    points: [
      '✅ Free LinkedIn Premium account included',
      '✅ Profile optimisation for #1 search ranking',
      '✅ Daily content generation (posts, carousels, newsletters)',
      '✅ Automated connection & follow‑up campaigns',
      '✅ Lead generation forms integrated with your CRM',
      '✅ Personal branding – turn employees into influencers'
    ],
    whyDifferent: 'KI analyses top LinkedIn creators in your niche and reverse‑engineers their engagement secrets.'
  },
  {
    id: 'ai',
    title: 'AI Marketing Automation',
    tagline: 'Sales funnels that work while you sleep',
    video: '/videos/ai_marketing_automation.webm',
    points: [
      '✅ WhatsApp chatbot for lead qualification',
      '✅ Email drip campaigns with personalised AI copy',
      '✅ Retargeting ads powered by predictive LTV models',
      '✅ Automated social proof – real‑time testimonials popups',
      '✅ AI calling agent for appointment setting',
      '✅ Full CRM integration (HubSpot, Salesforce, Pipedrive)'
    ],
    whyDifferent: 'Our automation uses distributed node intelligence – the more users, the smarter your funnels become.'
  }
];

export default function DigitalMarketingPage() {
  return (
    <>
      <AnimatedGradient />
      <div className="relative z-10 pt-28 pb-20 px-4 md:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Hero Section */}
          <ScrollReveal>
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-gold-400/30 bg-gold-400/5 text-gold-400 text-sm tracking-wider mb-6 backdrop-blur-sm">
                ✦ AI‑POWERED MARKETING ✦
              </div>
              <h1 className="text-6xl md:text-8xl font-serif mb-6">
                Marketing That <span className="text-gold-400">Thinks</span>
              </h1>
              <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                Intelligent, autonomous marketing solutions for businesses and professionals.
              </p>
            </div>
          </ScrollReveal>

          {/* Service Sections – each with video + bullet points + 2 CTAs */}
          {services.map((service, idx) => (
            <ScrollReveal key={service.id} delay={idx * 0.1}>
              <section id={service.id} className="mb-32 scroll-mt-24">
                <div className="glass-card rounded-3xl overflow-hidden">
                  <div className="grid md:grid-cols-2 gap-8 p-8 md:p-12">
                    {/* Left: Video */}
                    <div className="order-2 md:order-1">
                      <video
                        src={service.video}
                        autoPlay
                        loop
                        muted
                        playsInline
                        className="w-full rounded-2xl shadow-2xl border border-gold-400/30"
                        poster=""
                      >
                        <source src={service.video} type="video/webm" />
                        Your browser does not support the video tag.
                      </video>
                    </div>
                    {/* Right: Content */}
                    <div className="order-1 md:order-2">
                      <h2 className="text-3xl md:text-4xl font-serif mb-2">{service.title}</h2>
                      <p className="text-cyan-400 text-sm uppercase tracking-wider mb-4">{service.tagline}</p>
                      <ul className="space-y-2 mb-6">
                        {service.points.map((point, i) => (
                          <li key={i} className="flex items-start gap-2 text-gray-300 text-sm">
                            <span className="text-gold-400 mt-0.5">✦</span> {point}
                          </li>
                        ))}
                      </ul>
                      <div className="bg-cyan-400/10 p-4 rounded-xl mb-6 border-l-4 border-cyan-400">
                        <p className="text-sm italic text-gray-300">
                          <span className="font-bold text-cyan-400">Why we’re different:</span> {service.whyDifferent}
                        </p>
                      </div>
                      <div className="flex flex-wrap gap-4">
                        <Link
                          href="/support"
                          className="px-6 py-2 rounded-full border border-gold-400 text-gold-400 hover:bg-gold-400 hover:text-black transition"
                        >
                          Get Support
                        </Link>
                        <Link
                          href="/contact"
                          className="px-6 py-2 rounded-full bg-gradient-to-r from-gold-600 to-cyan-600 text-white hover:scale-105 transition"
                        >
                          Get Quote →
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            </ScrollReveal>
          ))}

          {/* Final CTA */}
          <ScrollReveal>
            <div className="text-center py-16">
              <h2 className="text-3xl md:text-5xl font-serif mb-4">Ready to dominate your market?</h2>
              <p className="text-gray-400 mb-8">Join 50+ businesses that grew with Kalki’s AI‑powered marketing.</p>
              <div className="flex flex-wrap gap-4 justify-center">
                <Link
                  href="/contact"
                  className="px-8 py-3 rounded-full bg-gradient-to-r from-gold-600 to-cyan-600 text-white font-semibold hover:scale-105 transition"
                >
                  Get a Free Marketing Audit
                </Link>
                <Link
                  href="/ki-cloud"
                  className="px-8 py-3 rounded-full border border-white/20 text-white hover:border-gold-400 transition"
                >
                  Explore KI Cloud Tools
                </Link>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </>
  );
}
