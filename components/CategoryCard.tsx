import { motion } from 'framer-motion';
import Link from 'next/link';

interface CategoryCardProps {
  title: string;
  description: string;
  features: string[];
  ctaText: string;
  ctaLink: string;
  gradient: string;
  delay: number;
}

export function CategoryCard({ title, description, features, ctaText, ctaLink, gradient, delay }: CategoryCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay, ease: 'easeOut' }}
      viewport={{ once: true, margin: '-50px' }}
      className="glass-card p-8 rounded-3xl group relative overflow-hidden"
    >
      <div className={`absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-700 bg-gradient-to-br ${gradient}`} />
      <div className="relative z-10">
        <h3 className="text-3xl font-serif text-white mb-4">{title}</h3>
        <p className="text-gray-300 mb-6 leading-relaxed">{description}</p>
        <ul className="space-y-3 mb-8">
          {features.map((feature, idx) => (
            <li key={idx} className="flex items-start gap-3 text-gray-400">
              <span className="text-gold-400 text-lg mt-0.5">✦</span>
              <span className="text-sm">{feature}</span>
            </li>
          ))}
        </ul>
        <Link
          href={ctaLink}
          className="inline-block px-6 py-3 rounded-full bg-gradient-to-r from-gold-600 to-cyan-600 text-white font-semibold hover:scale-105 transition-all duration-300"
        >
          {ctaText} →
        </Link>
      </div>
    </motion.div>
  );
}
