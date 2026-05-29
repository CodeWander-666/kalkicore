'use client';
import { useEffect } from 'react';

export default function StructuredData() {
  useEffect(() => {
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "Organization",
          "name": "Kalki Technologies",
          "alternateName": "Kalkicore",
          "url": "https://kalkicore.vercel.app",
          "logo": "https://kalkicore.vercel.app/favicon.svg",
          "sameAs": [
            "https://github.com/CodeWander-666",
            "https://wa.me/916261031710"
          ],
          "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+91-6261031710",
            "contactType": "customer service",
            "availableLanguage": ["English", "Hindi"]
          }
        },
        {
          "@type": "WebSite",
          "name": "Kalki Technologies",
          "url": "https://kalkicore.vercel.app",
          "potentialAction": {
            "@type": "SearchAction",
            "target": "https://kalkicore.vercel.app/support?q={search_term_string}",
            "query-input": "required name=search_term_string"
          }
        }
      ]
    });
    document.head.appendChild(script);
    return () => {
      document.head.removeChild(script);
    };
  }, []);

  return null;
}
