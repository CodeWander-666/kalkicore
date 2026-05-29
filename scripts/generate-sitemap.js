const fs = require('fs');
const path = require('path');

const SITE_URL = 'https://kalkicore.vercel.app';
const OUTPUT = 'public/sitemap.xml';

// Known static routes (add more as needed)
const staticRoutes = [
  '/', '/ki-cloud', '/digital-marketing', '/plans', '/about', '/vision',
  '/hiring', '/support', '/services', '/contact'
];

// Helper to scan app directory for page.tsx files
function scanAppDir(dir, baseRoute = '') {
  let routes = [];
  const items = fs.readdirSync(dir, { withFileTypes: true });
  for (const item of items) {
    const fullPath = path.join(dir, item.name);
    if (item.isDirectory()) {
      // Skip special directories
      if (item.name === 'api' || item.name === 'components' || item.name === 'lib') continue;
      const subRoutes = scanAppDir(fullPath, path.join(baseRoute, item.name));
      routes.push(...subRoutes);
    } else if (item.name === 'page.tsx' || item.name === 'page.jsx') {
      let route = baseRoute || '/';
      if (route !== '/' && !route.startsWith('/')) route = '/' + route;
      routes.push(route);
    }
  }
  return routes;
}

// Scan dynamic routes from app directory
let dynamicRoutes = [];
if (fs.existsSync('app')) {
  dynamicRoutes = scanAppDir('app');
  // Remove duplicates and sort
  dynamicRoutes = [...new Set(dynamicRoutes)].sort();
}

// Combine static and dynamic, remove duplicates
const allRoutes = [...new Set([...staticRoutes, ...dynamicRoutes])];

// Start XML
let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';

for (const route of allRoutes) {
  let priority = '0.5';
  let changefreq = 'monthly';
  if (route === '/') { priority = '1.0'; changefreq = 'weekly'; }
  else if (route === '/ki-cloud' || route === '/digital-marketing' || route === '/plans') { priority = '0.9'; changefreq = 'weekly'; }
  else if (route === '/services') { priority = '0.8'; changefreq = 'weekly'; }
  else if (route.startsWith('/services/')) { priority = '0.7'; changefreq = 'monthly'; }

  xml += `  <url>\n`;
  xml += `    <loc>${SITE_URL}${route}</loc>\n`;
  xml += `    <priority>${priority}</priority>\n`;
  xml += `    <changefreq>${changefreq}</changefreq>\n`;
  xml += `  </url>\n`;
}

xml += '</urlset>\n';

fs.writeFileSync(OUTPUT, xml);
console.log(`✅ Sitemap generated with ${allRoutes.length} URLs at ${OUTPUT}`);
