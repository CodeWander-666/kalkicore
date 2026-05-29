# SEO Guidelines for Kalki Technologies

## Internal Linking Strategy
- Every page should be reachable within 3 clicks from the homepage.
- Use descriptive anchor texts (e.g., "Learn about our SEO Dominant package").
- Regularly audit internal links using tools like Screaming Frog.

## Sitemap & Robots
- Sitemap is auto‑generated at `/sitemap.xml` and rebuilt on `npm run build`.
- Robots.txt is at `/robots.txt` – it disallows non‑essential paths and points to the sitemap.

## JSON‑LD Structured Data
- We inject Organization and WebSite schema via `<StructuredData />` component.
- This helps Google understand your brand and enables sitelinks search box.

## Updates
- After adding new pages, run `npm run build` (or `scripts/update-sitemap.sh`) to refresh the sitemap.
- Submit sitemap again in Google Search Console if you add many new pages.

## Monitoring
- Use Google Search Console for index coverage and crawl stats.
- Use Google Analytics 4 to track organic traffic.
- Monitor Core Web Vitals in GSC.

