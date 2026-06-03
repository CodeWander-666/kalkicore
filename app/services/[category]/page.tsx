import { notFound } from 'next/navigation';

const categories = ['for-startups', 'for-developers', 'for-small-businesses', 'for-social-creators'];

export async function generateStaticParams() {
  return categories.map(category => ({ category }));
}

export default function ServicePage({ params }: { params: { category: string } }) {
  if (!categories.includes(params.category)) notFound();
  return (
    <div className="pt-32 text-center">
      <h1 className="text-4xl font-serif capitalize">{params.category.replace(/-/g, ' ')}</h1>
      <p className="text-gray-400 mt-4">This service page is coming soon.</p>
      <a href="/services" className="inline-block mt-6 text-gold-400 hover:underline">← Back to all services</a>
    </div>
  );
}
