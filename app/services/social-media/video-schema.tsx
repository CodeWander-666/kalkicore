'use client';
import { useEffect } from 'react';

export default function VideoSchema() {
  useEffect(() => {
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "VideoObject",
      "name": "social-media demo",
      "description": "See how social-media works – AI‑powered digital marketing.",
      "thumbnailUrl": "https://kalkicore.vercel.app/videos/social-media.jpg",
      "contentUrl": "https://kalkicore.vercel.app/videos/social-media.webm",
      "uploadDate": "2025-01-01T00:00:00Z",
      "duration": "PT1M",
      "embedUrl": "https://kalkicore.vercel.app/videos/social-media.webm"
    });
    document.head.appendChild(script);
    return () => { document.head.removeChild(script); };
  }, []);
  return null;
}
