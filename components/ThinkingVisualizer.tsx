import { useKI } from '@/context/KIContext';
import { motion } from 'framer-motion';

export function ThinkingVisualizer() {
  const { activeNodes } = useKI();

  return (
    <div className="flex flex-col gap-2 p-3 min-w-[200px]">
      <div className="flex items-center gap-2 text-xs text-cyan-400">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400" />
        </span>
        <span>Real distributed network</span>
      </div>

      <div className="flex items-baseline gap-1 justify-center">
        <span className="text-2xl font-mono font-bold text-gold-400">
          {activeNodes}
        </span>
        <span className="text-xs text-gray-400">active nodes</span>
      </div>

      <div className="h-8 text-center text-xs text-gray-500">
        {activeNodes > 1 ? 'Ensemble active – answers are voted by multiple nodes' : 'Waiting for more nodes...'}
      </div>

      <div className="flex gap-1 justify-center">
        {[...Array(Math.min(5, activeNodes))].map((_, i) => (
          <motion.div
            key={i}
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ repeat: Infinity, duration: 1.2, delay: i * 0.15 }}
            className="w-1.5 h-1.5 rounded-full bg-cyan-400"
          />
        ))}
      </div>
    </div>
  );
}
