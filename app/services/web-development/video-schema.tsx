'use client';
import { useEffect } from 'react';

export default function VideoSchema() {
  useEffect(() => {
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "VideoObject",
      "name": "web-development demo",
      "description": "See how web-development works – AI‑powered digital marketing.",
      "thumbnailUrl": "https://kalkicore.vercel.app/videos/web-development.jpg",
      "contentUrl": "https://kalkicore.vercel.app/videos/web-development.webm",
      "uploadDate": "2025-01-01T00:00:00Z",
      "duration": "PT1M",
      "embedUrl": "https://kalkicore.vercel.app/videos/web-development.webm"
    });
    document.head.appendChild(script);
    return () => { document.head.removeChild(script); };
  }, []);
  return null;
}
