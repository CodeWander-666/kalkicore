import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function GET() {
  try {
    const oneHourAgo = Date.now() - 3600000;
    const { data, error } = await supabase
      .from('nodes')
      .select('id, device_name, cpu_cores, memory, benchmark, last_seen')
      .gt('last_seen', oneHourAgo)
      .order('last_seen', { ascending: false });

    if (error) throw error;
    return NextResponse.json(data || []);
  } catch (err) {
    console.error(err);
    return NextResponse.json([], { status: 500 });
  }
}
