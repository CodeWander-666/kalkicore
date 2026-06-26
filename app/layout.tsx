import './globals.css';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Kalki Technologies – The New Era of Private AI',
  description: 'Kalki Technologies is redefining AI. Our new era is defined on kalki-intelligence.in – the future of open‑source, private intelligence.',
  robots: 'index, follow',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
