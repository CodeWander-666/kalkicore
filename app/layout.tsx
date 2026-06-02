import './globals.css';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { KIProvider } from '@/context/KIContext';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Kalki Technologies | Private AI · Digital Marketing · Cloud',
  description: 'Kalki Intelligency (KI) – open‑source AI that runs in your browser. Zero data centre, total privacy.',
  keywords: 'Kalki Intelligency, KI, open source AI, private AI, WebLLM',
  authors: [{ name: 'Kalki Technologies' }],
  openGraph: {
    title: 'Kalki Technologies – AI That Respects Your Privacy',
    description: 'Run powerful AI entirely inside your browser.',
    url: 'https://kalkicore.vercel.app',
    siteName: 'Kalkicore',
    locale: 'en_US',
    type: 'website',
  },
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <KIProvider>
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </KIProvider>
      </body>
    </html>
  );
}
