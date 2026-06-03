import { motion } from 'framer-motion';
import Link from 'next/link';

interface ServiceCardProps {
  title: string;
  description: string;
  href: string;
  icon: React.ReactNode;
  gradient: string;
}

export function ServiceCard({ title, description, href, icon, gradient }: ServiceCardProps) {
  return (
    <motion.div
      whileHover={{ y: -8, scale: 1.02 }}
      transition={{ duration: 0.3 }}
      className="glass-card p-6 group relative overflow-hidden"
    >
      <div className={`absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-500 bg-gradient-to-br ${gradient}`} />
      <div className="relative z-10">
        <div className="text-5xl mb-4">{icon}</div>
        <h3 className="text-xl font-serif text-white mb-2">{title}</h3>
        <p className="text-gray-400 text-sm mb-4 leading-relaxed">{description}</p>
        <Link href={href} className="text-gold-400 text-sm hover:text-gold-300 inline-flex items-center gap-1">
          Discover <span className="text-lg">→</span>
        </Link>
      </div>
    </motion.div>
  );
}
