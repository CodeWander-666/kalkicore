#!/bin/bash
set -euo pipefail

echo "🎯 Elevating brand presence with large label and tagline..."

cat > app/page.tsx << 'EOF'
'use client';
import { useEffect, useRef } from 'react';

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    // Redirect to the new site after 4 seconds
    const timer = setTimeout(() => {
      window.location.href = 'https://www.kalki-intelligence.in/';
    }, 4000);

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let w = window.innerWidth;
    let h = window.innerHeight;
    canvas.width = w;
    canvas.height = h;

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+{}:<>?~';
    const charArray = chars.split('');
    const columns = Math.floor(w / 14);
    const drops: number[] = [];
    const speeds: number[] = [];
    const charLengths: number[] = [];

    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * -h;
      speeds[i] = 2 + Math.random() * 4;
      charLengths[i] = 10 + Math.floor(Math.random() * 20);
    }

    const colors = ['#00ffff', '#ff00ff'];

    function draw() {
      ctx.fillStyle = 'rgba(10, 10, 15, 0.05)';
      ctx.fillRect(0, 0, w, h);

      for (let i = 0; i < columns; i++) {
        const color = colors[i % 2];
        ctx.fillStyle = color;
        ctx.font = '14px "Courier New", monospace';
        ctx.shadowColor = color;
        ctx.shadowBlur = 8;

        const charCount = charLengths[i];
        for (let j = 0; j < charCount; j++) {
          const char = charArray[Math.floor(Math.random() * charArray.length)];
          const x = i * 14;
          const y = drops[i] - j * 16;
          const opacity = 1 - (j / charCount);
          ctx.globalAlpha = opacity * 0.8;
          ctx.fillText(char, x, y);
        }
        ctx.globalAlpha = 1;

        drops[i] += speeds[i];

        if (drops[i] - charLengths[i] * 16 > h) {
          drops[i] = -charLengths[i] * 16;
          speeds[i] = 2 + Math.random() * 4;
          charLengths[i] = 10 + Math.floor(Math.random() * 20);
        }
      }

      requestAnimationFrame(draw);
    }

    draw();

    const handleResize = () => {
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = w;
      canvas.height = h;
      const newColumns = Math.floor(w / 14);
      if (newColumns > drops.length) {
        for (let i = drops.length; i < newColumns; i++) {
          drops[i] = Math.random() * -h;
          speeds[i] = 2 + Math.random() * 4;
          charLengths[i] = 10 + Math.floor(Math.random() * 20);
        }
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <>
      {/* Background canvas */}
      <canvas ref={canvasRef} style={{ position: 'fixed', inset: 0, zIndex: 0, background: '#0a0a0f' }} />

      {/* Foreground content – large, bold brand display */}
      <div style={{
        position: 'fixed',
        inset: 0,
        zIndex: 10,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        pointerEvents: 'none',
        fontFamily: "'Courier New', monospace",
        padding: '2rem',
      }}>
        {/* Main brand name – large, bold, with gradient and glow */}
        <h1 style={{
          fontSize: 'clamp(4rem, 12vw, 8rem)',
          fontWeight: 900,
          background: 'linear-gradient(135deg, #00ffff, #ff00ff, #00ffff)',
          backgroundSize: '300% 300%',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          animation: 'shimmer 4s ease infinite',
          letterSpacing: '0.15em',
          textShadow: '0 0 40px rgba(0,255,255,0.2), 0 0 80px rgba(255,0,255,0.1)',
          marginBottom: '0.5rem',
          lineHeight: '1.1',
        }}>
          KALKI
          <br />
          TECHNOLOGIES
        </h1>

        {/* Tagline */}
        <p style={{
          fontSize: 'clamp(1.2rem, 2.5vw, 2.5rem)',
          color: '#ffffff',
          letterSpacing: '0.3em',
          textTransform: 'uppercase',
          background: 'linear-gradient(135deg, rgba(0,255,255,0.6), rgba(255,0,255,0.6))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: 300,
          marginTop: '0.5rem',
          textShadow: '0 0 30px rgba(0,255,255,0.15)',
          padding: '0.5rem 2rem',
          borderTop: '1px solid rgba(255,255,255,0.08)',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}>
          The New Era of Intelligence
        </p>

        {/* Domain display with redirect note */}
        <div style={{
          marginTop: '2.5rem',
          fontSize: 'clamp(1rem, 1.5vw, 1.6rem)',
          color: 'rgba(255,255,255,0.6)',
          letterSpacing: '0.15em',
          border: '1px solid rgba(0,255,255,0.15)',
          padding: '0.8rem 2rem',
          borderRadius: '4px',
          background: 'rgba(0,0,0,0.3)',
          backdropFilter: 'blur(4px)',
        }}>
          <span style={{ color: '#00ffff' }}>⟡</span>
          {' '}
          kalki-intelligence.in
          {' '}
          <span style={{ color: '#ff00ff' }}>⟡</span>
        </div>

        {/* Redirect timer */}
        <div style={{
          marginTop: '2rem',
          fontSize: '0.9rem',
          color: 'rgba(255,255,255,0.25)',
          animation: 'pulse 1.5s ease-in-out infinite',
          letterSpacing: '0.15em',
        }}>
          ◈ REDIRECTING IN 4 SECONDS ◈
        </div>
      </div>

      <style>{`
        @keyframes shimmer {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.2; }
          50% { opacity: 0.8; }
        }
        body { margin: 0; overflow: hidden; background: #0a0a0f; }
      `}</style>
    </>
  );
}
EOF

# Rebuild
rm -rf .next
npm run build

echo ""
echo "✅ Done! The page now features a bold, large-format brand display with tagline."
echo "🌐 It will redirect to https://www.kalki-intelligence.in/ after 4 seconds."