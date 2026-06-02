import { NextResponse } from 'next/server';
import { redis } from '@/lib/redis';
import { supabaseAdmin } from '@/lib/supabase';

let heartbeatCounter = 0;

export async function POST(req: Request) {
  try {
    const { nodeId, deviceName, cpuCores, memory, benchmark } = await req.json();
    if (!nodeId) return NextResponse.json({ error: 'Missing nodeId' }, { status: 400 });

    const now = Date.now();

    // Redis heartbeat (fast, real‑time presence)
    const key = `node:${nodeId}`;
    await redis.hset(key, {
      lastSeen: now,
      cpuCores: cpuCores || 2,
      memory: memory || 4,
      benchmark: benchmark || 100,
    });
    await redis.expire(key, 60);

    // Supabase persistent storage (device specs)
    const { error: supabaseError } = await supabaseAdmin
      .from('nodes')
      .upsert({
        id: nodeId,
        device_name: deviceName || 'Unknown device',
        cpu_cores: cpuCores || 2,
        memory: memory || 4,
        benchmark: benchmark || 100,
        last_seen: now,
        created_at: now,
      }, { onConflict: 'id' });

    if (supabaseError) console.warn('Supabase upsert failed:', supabaseError);

    // Trigger cleanup every 50 heartbeats (fire-and-forget, but await to avoid error)
    heartbeatCounter++;
    if (heartbeatCounter % 50 === 0) {
      try {
        await supabaseAdmin.rpc('cleanup_old_nodes');
      } catch (cleanupErr) {
        console.warn('Cleanup failed:', cleanupErr);
      }
    }

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: 'Server error' }, { status: 500 });
  }
}
