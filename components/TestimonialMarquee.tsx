import { motion } from 'framer-motion';

const testimonials = [
  { text: "Kalki's AI engine transformed our digital presence completely.", author: "Alex Morgan, CEO" },
  { text: "The most elegant AI platform we've ever used.", author: "Sarah Chen, CMO" },
  { text: "Zero upfront cost, world-class service. Kalki is the future.", author: "David Kumar, Founder" },
  { text: "The 3D interactive experience is unmatched.", author: "Elena Rossi, Director" },
];

export function TestimonialMarquee() {
  return (
    <div className="overflow-hidden py-8">
      <motion.div
        animate={{ x: ['0%', '-100%'] }}
        transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
        className="flex gap-6 w-max"
      >
        {[...testimonials, ...testimonials].map((t, i) => (
          <div key={i} className="glass-card w-96 p-8">
            <div className="flex gap-1 mb-4">{[...Array(5)].map((_, j) => (<svg key={j} className="w-4 h-4 text-gold-400 fill-gold-400" viewBox="0 0 20 20"><path d="M10 15l-5.5 3 1.5-6-4-3.5 6-.5L10 2l2 5.5 6 .5-4 3.5 1.5 6z"/></svg>))}</div>
            <p className="text-gray-300 italic leading-relaxed">"{t.text}"</p>
            <p className="mt-6 text-gold-400 font-semibold">{t.author}</p>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
