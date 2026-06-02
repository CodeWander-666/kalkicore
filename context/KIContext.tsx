'use client';
import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { CreateMLCEngine } from '@mlc-ai/web-llm';

const MODEL_ID = 'SmolLM2-135M-Instruct-q0f16-MLC';
const NODE_ID_KEY = 'ki_node_id';

interface KIContextType {
  engine: any | null;
  loading: boolean;
  activeNodes: number;
  totalPower: number;
}

const KIContext = createContext<KIContextType | undefined>(undefined);

async function fetchWithRetry(url: string, retries = 3, delay = 1000): Promise<any> {
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      if (i === retries - 1) throw err;
      await new Promise(r => setTimeout(r, delay * (i + 1)));
    }
  }
}

export function KIProvider({ children }: { children: ReactNode }) {
  const [engine, setEngine] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeNodes, setActiveNodes] = useState(0);
  const [totalPower, setTotalPower] = useState(0);

  // Register node with device specs (unchanged)
  useEffect(() => {
    let nodeId = localStorage.getItem(NODE_ID_KEY);
    if (!nodeId) {
      nodeId = crypto.randomUUID();
      localStorage.setItem(NODE_ID_KEY, nodeId);
    }

    const cpuCores = navigator.hardwareConcurrency || 2;
    const memory = (navigator as any).deviceMemory || 4;
    const benchmark = 150;

    const register = () => {
      fetch('/api/node/heartbeat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodeId, cpuCores, memory, benchmark }),
      }).catch(e => console.warn('Heartbeat failed:', e));
    };
    register();
    const interval = setInterval(register, 30000);
    window.addEventListener('beforeunload', () => {
      fetch('/api/node/unregister', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodeId }),
      });
    });
    return () => clearInterval(interval);
  }, []);

  // Poll node count with retries – start after 2 seconds to allow API to warm up
  useEffect(() => {
    let isMounted = true;
    let interval: NodeJS.Timeout;

    const pollCount = async () => {
      try {
        const data = await fetchWithRetry('/api/node/count', 2, 500);
        if (isMounted) {
          setActiveNodes(data.count || 0);
          setTotalPower(data.power || 0);
        }
      } catch (err) {
        console.warn('Node count poll failed (will retry):', err);
        if (isMounted) {
          setActiveNodes(0);
          setTotalPower(0);
        }
      }
    };

    // Wait 2 seconds before first poll to let server settle
    const initialTimeout = setTimeout(() => {
      pollCount();
      interval = setInterval(pollCount, 5000);
    }, 2000);

    return () => {
      isMounted = false;
      clearTimeout(initialTimeout);
      if (interval) clearInterval(interval);
    };
  }, []);

  // Load WebLLM engine (unchanged)
  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        const eng = await CreateMLCEngine(MODEL_ID, { initProgressCallback: () => {} });
        if (mounted) {
          setEngine(eng);
          setLoading(false);
        }
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };
    load();
    return () => { mounted = false; };
  }, []);

  return (
    <KIContext.Provider value={{ engine, loading, activeNodes, totalPower }}>
      {children}
    </KIContext.Provider>
  );
}

export const useKI = () => {
  const ctx = useContext(KIContext);
  if (!ctx) throw new Error('useKI must be used within KIProvider');
  return ctx;
};
