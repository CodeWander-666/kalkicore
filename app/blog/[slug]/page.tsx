'use client'
import { AnimatedGradientBackground } from '@/components/AnimatedGradientBackground';
import { ScrollReveal } from '@/components/ScrollReveal';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { useParams } from 'next/navigation';

// This is a simplified version – in production you'd fetch from CMS or markdown files.
const blogContent = {
  "rise-of-private-ai": {
    title: "The Rise of Private AI: Why Your Browser Is the New Cloud",
    content: `
      <p>The era of centralised AI is ending. Users are increasingly aware that every prompt sent to ChatGPT, Claude, or Gemini is stored, analysed, and often used for training. Kalki Technologies offers a radical alternative: AI that runs entirely inside your browser.</p>
      <p>Using WebLLM, we can run a 135M parameter model (SmolLM2) on any modern device – no GPU required. This is not a demo; it's production‑grade AI that respects your privacy by design. Your conversations never leave your device.</p>
      <p>The distributed node network further amplifies this: every visitor contributes to a global "thinking pool", but no personal data is ever shared. More nodes = smarter AI, but still zero data leakage.</p>
      <p>This is the future of AI – open, private, and owned by the people.</p>
    `,
  },
  "programmatic-seo-case-study": {
    title: "Programmatic SEO at Scale: A Case Study",
    content: `<p>We helped a travel agency scale from 200 to 10,000 landing pages using KI‑generated content. The result? 400% increase in organic traffic within 3 months, with zero manual writing.</p><p>Programmatic SEO is not just about bulk – it's about relevance. Our AI generates unique, value‑driven content for each city, neighbourhood, and service combination. Google loves it because it answers specific user intent.</p><p>Read the full methodology in our upcoming whitepaper.</p>`,
  },
  "deepseek-like-chatbot-webllm": {
    title: "Building a DeepSeek‑like Chatbot with WebLLM",
    content: `<p>In this technical guide, we show you how to replicate the entire KI Bot interface – local inference, message streaming, conversation persistence, and a glowing animated border – using only Next.js and WebLLM. No external APIs, no server costs.</p><p>The full source code is available on our GitHub. Clone, deploy, and have your own private AI assistant in minutes.</p>`,
  },
  "gmb-seo-roi": {
    title: "Why GMB SEO Is Still the Best ROI for Local Businesses",
    content: `<p>Google Business Profile optimisation delivers an average 10x return on investment for local service businesses. A single #1 ranking can generate 50+ extra calls per week.</p><p>We break down our exact process: complete profile optimisation, review generation, local citations, and AI‑powered Q&A management. Results are often visible within 30 days.</p>`,
  },
  "instagram-viral-automation": {
    title: "Automating Instagram Reels with AI – Our Viral Formula",
    content: `<p>Viral content is not luck; it's pattern recognition. Our AI analyses millions of Reels daily to predict what will trend next week. We then generate scripts, captions, and editing suggestions.</p><p>Our clients see an average of 2 viral posts per month (over 500k views). This automation is included in our Social Media Automation package – ₹9,999/month.</p>`,
  },
  "open-source-ai-manifesto": {
    title: "Open Source vs Proprietary AI: The Kalki Manifesto",
    content: `<p>We believe AI is a public good, not a commodity to be locked behind paywalls and data harvesting. All our code is open source (MIT license). You can audit, fork, and contribute.</p><p>The Kalki Manifesto outlines our commitment: transparency, privacy, and community ownership. Join us in building a better AI future.</p>`,
  },
};

export default function BlogPostPage() {
  const params = useParams();
  const slug = params.slug as string;
  const post = blogContent[slug as keyof typeof blogContent];

  if (!post) notFound();

  return (
    <>
      <AnimatedGradientBackground />
      <div className="relative z-10 pt-28 pb-20 px-4 md:px-8">
        <div className="max-w-4xl mx-auto">
          <Link href="/blog" className="text-gold-400 text-sm mb-6 inline-block">← Back to blog</Link>
          <ScrollReveal>
            <h1 className="text-5xl md:text-6xl font-serif mb-6">{post.title}</h1>
            <div className="glass-card rounded-3xl p-8 md:p-12 prose prose-invert max-w-none">
              <div dangerouslySetInnerHTML={{ __html: post.content }} />
            </div>
          </ScrollReveal>
        </div>
      </div>
    </>
  );
}
