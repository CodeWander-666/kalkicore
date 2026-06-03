'use client';
import { useEffect } from 'react';

export default function VideoSchema() {
  useEffect(() => {
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "VideoObject",
      "name": "linkedin demo",
      "description": "See how linkedin works – AI‑powered digital marketing.",
      "thumbnailUrl": "https://kalkicore.vercel.app/videos/linkedin.jpg",
      "contentUrl": "https://kalkicore.vercel.app/videos/linkedin.webm",
      "uploadDate": "2025-01-01T00:00:00Z",
      "duration": "PT1M",
      "embedUrl": "https://kalkicore.vercel.app/videos/linkedin.webm"
    });
    document.head.appendChild(script);
    return () => { document.head.removeChild(script); };
  }, []);
  return null;
}
