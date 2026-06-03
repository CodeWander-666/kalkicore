import { useKI } from '@/context/KIContext';

export function NodeTracker({ compact = false }: { compact?: boolean }) {
  const { activeNodes, totalPower } = useKI();

  if (compact) {
    return (
      <div className="flex items-center gap-1.5 text-xs">
        <span className="relative flex h-1.5 w-1.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-400" />
        </span>
        <span className="text-gold-400 font-mono font-bold">{activeNodes}</span>
        <span className="text-gray-400">nodes</span>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/40 backdrop-blur-sm border border-gold-400/30">
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-400" />
      </span>
      <span className="text-gold-400 font-mono text-sm font-bold">{activeNodes}</span>
      <span className="text-[10px] text-gray-400">active nodes</span>
      <span className="text-[10px] text-cyan-400 ml-1">⚡{Math.floor(totalPower/1000)}k ops</span>
    </div>
  );
}
