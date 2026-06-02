import { NextResponse } from 'next/server';
import { redis } from '@/lib/redis';
import { supabase } from '@/lib/supabase';

export async function GET() {
  try {
    // Get active nodes from Redis (real‑time)
    const keys = await redis.keys('node:*');
    let activeNodes = 0;
    for (const key of keys) {
      const node = await redis.hgetall(key);
      if (node && node.lastSeen && Date.now() - Number(node.lastSeen) < 60000) {
        activeNodes++;
      }
    }

    // Get total power from Supabase (for display)
    const oneHourAgo = Date.now() - 3600000;
    const { data, error } = await supabase
      .from('nodes')
      .select('cpu_cores, benchmark')
      .gt('last_seen', oneHourAgo);
    if (error) throw error;
    const totalPower = data.reduce((sum, node) => sum + (node.cpu_cores || 1) * (node.benchmark || 100), 0);

    return NextResponse.json({ count: activeNodes, power: totalPower });
  } catch (err) {
    console.error(err);
    return NextResponse.json({ count: 0, power: 0 });
  }
}
