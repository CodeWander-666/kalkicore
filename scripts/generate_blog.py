#!/usr/bin/env python3
"""
SIDDHI AI - Enhanced Automated Blog Generator
Produces high-quality, unique, SEO-optimized blog posts daily.
"""

import os
import random
import datetime
import re
import requests
import logging
import sys
import time
from string import punctuation
from typing import List, Tuple, Optional

# -------------------- CONFIGURATION --------------------
SITE_URL = "https://siddhiai-welcome.vercel.app"
BLOG_DIR = "blog"
POSTS_DIR = os.path.join(BLOG_DIR, "posts")
INDEX_FILE = os.path.join(BLOG_DIR, "index.html")
LOG_FILE = "blog_generator.log"

# Path to your main index.html (to extract keywords)
INDEX_HTML_PATH = "index.html"

# API endpoints
DATAMUSE_API = "https://api.datamuse.com/words"
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 2

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# -------------------- LOCATION DATA --------------------
GLOBAL_LOCATIONS = [
    "United States", "Canada", "United Kingdom", "Australia",
    "New Zealand", "Ireland"
]

COUNTRY = "India"

STATES = {
    "Madhya Pradesh": ["Indore", "Bhopal", "Gwalior", "Jabalpur", "Ujjain"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"]
}

AREAS = {
    "Indore": ["Vijay Nagar", "New Palasia", "Scheme No. 78", "Rajendra Nagar", "Bholaram"],
    "Bangalore": ["Indiranagar", "Whitefield", "Koramangala", "HSR Layout", "Jayanagar"]
}

# -------------------- UTILITY FUNCTIONS --------------------
def slugify(text: str) -> str:
    """Convert text to URL‑friendly slug."""
    text = text.lower().replace(" ", "-")
    text = re.sub(rf"[{re.escape(punctuation)}]", "", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")

def fetch_with_retry(url: str, params: dict = None) -> Optional[requests.Response]:
    """Fetch URL with exponential backoff retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt))
            else:
                logger.error(f"All retries failed for URL: {url}")
                return None

def get_lsi_keywords(phrase: str, max_results: int = 5) -> List[str]:
    """Fetch semantically related keywords from Datamuse API."""
    try:
        params = {'ml': phrase, 'max': max_results}
        response = fetch_with_retry(DATAMUSE_API, params=params)
        if response and response.status_code == 200:
            data = response.json()
            keywords = [item['word'] for item in data if 'word' in item]
            logger.info(f"Found {len(keywords)} LSI keywords for '{phrase}'")
            return keywords
    except Exception as e:
        logger.error(f"Error fetching LSI keywords: {e}")
    return []

def safe_read_file(filepath: str) -> Optional[str]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return None

def safe_write_file(filepath: str, content: str) -> bool:
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully wrote file: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error writing file {filepath}: {e}")
        return False

# -------------------- KEYWORD EXTRACTION --------------------
def extract_keywords_from_index() -> List[str]:
    """Parse the hidden SEO keywords div from index.html."""
    content = safe_read_file(INDEX_HTML_PATH)
    if not content:
        logger.warning("Could not read index.html; using default keywords.")
        return []
    
    pattern = r'<div style="display:none;">(.*?)</div>'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        logger.warning("No hidden keywords div found in index.html.")
        return []
    
    keywords_text = match.group(1)
    keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    logger.info(f"Extracted {len(unique_keywords)} unique keywords from index.html")
    return unique_keywords

MASTER_KEYWORDS = extract_keywords_from_index() or [
    "learn python for beginners", "digital marketing agency in india", "web development",
    "SEO services", "AI solutions", "stock market analysis", "Python training"
]

# -------------------- LOCATION SELECTION --------------------
def select_location() -> Tuple[str, str]:
    levels = ['global', 'country', 'state', 'city', 'area']
    weights = [0.1, 0.2, 0.2, 0.3, 0.2]
    level = random.choices(levels, weights=weights)[0]
    if level == 'global':
        return random.choice(GLOBAL_LOCATIONS), "global"
    elif level == 'country':
        return COUNTRY, "country"
    elif level == 'state':
        state = random.choice(list(STATES.keys()))
        return state, "state"
    elif level == 'city':
        state = random.choice(list(STATES.keys()))
        city = random.choice(STATES[state])
        return f"{city}, {state}", "city"
    else:
        city = random.choice(list(AREAS.keys()))
        area = random.choice(AREAS[city])
        return f"{area}, {city}", "area"

# -------------------- CONTENT GENERATION --------------------
def generate_intro(primary_kw: str, location: str, lsi_keywords: List[str]) -> str:
    lsi_phrase = ", ".join(lsi_keywords[:3]) if lsi_keywords else primary_kw
    year = datetime.datetime.now().year
    return f"""<p>Are you searching for the best <strong>{primary_kw} in {location}</strong>? You've come to the right place. At <strong>SIDDHI AI</strong>, we specialize in delivering world-class {primary_kw} services tailored to businesses and individuals in {location}. With our proven track record and cutting-edge technology, we've helped hundreds of clients achieve their digital goals.</p>

<p>In this comprehensive guide, we'll explore everything you need to know about {primary_kw} in {location}, including local trends, pricing, expert tips, and how SIDDHI AI can help you succeed in {year}.</p>"""

def generate_why_location(primary_kw: str, location: str, lsi_keywords: List[str]) -> str:
    lsi_phrase = ", ".join(lsi_keywords[:3]) if lsi_keywords else primary_kw
    return f"""<h2>Why {location} is a Prime Destination for {primary_kw.title()}</h2>
<p>{location} has emerged as a thriving hub for digital innovation and business growth. With a rapidly expanding economy and increasing demand for professional {primary_kw.lower()} services, now is the ideal time to invest in {primary_kw}. Local businesses in {location} are leveraging {lsi_phrase} to gain competitive advantages and reach wider audiences.</p>

<p>SIDDHI AI understands the unique dynamics of the {location} market. Our team combines global expertise with local insights to deliver solutions that resonate with your target audience. Whether you're a startup, SME, or enterprise, we have the right strategy for you.</p>"""

def generate_benefits(primary_kw: str, location: str) -> str:
    benefits_pool = [
        f"<strong>✓ Local Market Expertise:</strong> We understand {location}'s business landscape and consumer behavior.",
        f"<strong>✓ Customized Solutions:</strong> Tailored {primary_kw} strategies for {location}'s unique requirements.",
        f"<strong>✓ Proven Results:</strong> Track record of successful projects across {location}.",
        f"<strong>✓ Cost-Effective:</strong> Competitive pricing without compromising on quality.",
        f"<strong>✓ Ongoing Support:</strong> 24/7 assistance from our {location}-based team.",
        f"<strong>✓ Data-Driven Approach:</strong> We use analytics to continuously optimize your campaigns.",
        f"<strong>✓ Award-Winning Team:</strong> Recognized experts in {primary_kw} and digital innovation."
    ]
    selected = random.sample(benefits_pool, min(6, len(benefits_pool)))
    items = "".join(f"<li>{item}</li>" for item in selected)
    return f"""<h2>Key Benefits of Professional {primary_kw.title()} in {location}</h2>
<ul class="space-y-3">{items}</ul>"""

def generate_services(primary_kw: str, location: str) -> str:
    services_list = [
        f"<strong>🔹 Complete {primary_kw} Packages:</strong> End-to-end solutions for startups and enterprises.",
        f"<strong>🔹 Custom Strategy Development:</strong> Tailored approaches for your specific goals.",
        f"<strong>🔹 Implementation & Management:</strong> Full-service execution with regular updates.",
        f"<strong>🔹 Analytics & Reporting:</strong> Detailed insights into your campaign performance.",
        f"<strong>🔹 Training & Workshops:</strong> Hands-on {primary_kw} training for your team in {location}.",
        f"<strong>🔹 24/7 Support:</strong> Round-the-clock assistance from our experts."
    ]
    items = "".join(f"<li>{item}</li>" for item in services_list)
    return f"""<h2>Our {primary_kw.title()} Services in {location}</h2>
<p>SIDDHI AI offers comprehensive {primary_kw} solutions designed for businesses in {location}:</p>
<ul class="space-y-2">{items}</ul>"""

def generate_faqs(primary_kw: str, location: str, areas_str: str) -> str:
    faq_pool = [
        (f"❓ How much does {primary_kw} cost in {location}?",
         f"Prices vary based on project scope and requirements. Contact SIDDHI AI for a free, no-obligation quote tailored to your needs."),
        (f"❓ Why choose SIDDHI AI for {primary_kw} in {location}?",
         f"SIDDHI AI combines international standards with local expertise. We're verified (GST & Udyam), have 66+ global clients, and offer 24/7 support from our {location} team."),
        (f"❓ How quickly can I see results?",
         f"Timelines depend on the specific service. Typically, clients see initial improvements within 2-3 months of starting our {primary_kw} services."),
        (f"❓ Do you serve specific areas within {location}?",
         f"Yes! We serve all areas including {areas_str}."),
        (f"❓ What industries do you specialize in?",
         f"We work with a wide range of industries including e-commerce, healthcare, education, real estate, and technology."),
        (f"❓ Can I get a customized package?",
         f"Absolutely! We tailor our services to meet your unique business needs and budget.")
    ]
    selected = random.sample(faq_pool, min(5, len(faq_pool)))
    faq_html = ""
    for q, a in selected:
        faq_html += f"""
    <div>
        <h3>{q}</h3>
        <p>{a}</p>
    </div>"""
    return f"""<h2>Frequently Asked Questions About {primary_kw} in {location}</h2>
<div class="space-y-6">{faq_html}</div>"""

def generate_success_story(primary_kw: str, location: str) -> str:
    stories = [
        (f"Startup in {location}", f"increased their website traffic by 200% and doubled sales within 6 months using our {primary_kw} services."),
        (f"Local e‑commerce store", f"achieved a 150% boost in conversions after implementing our {primary_kw} strategies."),
        (f"Educational institution", f"saw a 300% increase in course enrollments through targeted {primary_kw} campaigns."),
        (f"Real estate agency", f"generated 80+ qualified leads per month with our {primary_kw} expertise."),
    ]
    client, result = random.choice(stories)
    return f"""<h2>Success Story: {client}</h2>
<p>A {client} in {location} partnered with SIDDHI AI to transform their online presence through our {primary_kw} services. Within months, they {result}</p>"""

def generate_cta(primary_kw: str, location: str) -> str:
    return f"""<div class="text-center my-12">
    <p class="text-lg mb-6">Ready to dominate {primary_kw} in {location}? Let's talk!</p>
    <a href="/#contact" class="btn-creepy inline-flex bg-accent text-obsidian px-8 py-4 rounded-full text-[10px] font-black uppercase tracking-[0.2em] transition-all hover:bg-textmain shadow-[0_0_20px_rgba(var(--accent-rgb),0.2)]">
        <span class="btn-text-content">Free Consultation</span>
        <div class="eyes-wrapper">
            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
        </div>
    </a>
</div>"""

def generate_related_posts(current_post_filename: str) -> str:
    """Generate a list of links to other blog posts (excluding current)."""
    posts = []
    if os.path.exists(POSTS_DIR):
        all_posts = [f for f in os.listdir(POSTS_DIR) if f.endswith('.html') and f != current_post_filename]
        selected = random.sample(all_posts, min(3, len(all_posts))) if all_posts else []
        for fname in selected:
            content = safe_read_file(os.path.join(POSTS_DIR, fname))
            if content:
                title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
                title = title_match.group(1).strip() if title_match else fname.replace('.html', '').replace('-', ' ').title()
                posts.append((title, f"/blog/posts/{fname}"))
    if not posts:
        return ""
    
    links = "".join(f'<li><a href="{url}" class="hover:text-accent transition-colors">{title}</a></li>' for title, url in posts)
    return f"""
<div class="mt-16 pt-8 border-t border-textmain/10">
    <h3 class="text-2xl font-serif mb-6">Related Articles</h3>
    <ul class="space-y-2">{links}</ul>
</div>"""

def generate_article(primary_kw: str, location: str) -> Tuple[str, str, str]:
    year = datetime.datetime.now().year
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    title_templates = [
        f"Best {primary_kw} in {location} – {year} Complete Guide",
        f"Top {primary_kw} Services in {location}: {year} Review",
        f"How to Choose the Right {primary_kw} in {location} ({year})",
        f"{primary_kw} in {location}: Expert Tips & Strategies for {year}",
        f"The Ultimate Guide to {primary_kw} in {location} ({year})"
    ]
    title = random.choice(title_templates)
    
    meta_description = f"Looking for expert {primary_kw} in {location}? SIDDHI AI provides top-rated {primary_kw.lower()} solutions. Free consultation! ⭐⭐⭐⭐⭐"
    
    lsi_keywords = get_lsi_keywords(f"{primary_kw} {location}")
    
    if ',' in location:
        city = location.split(',')[0].strip()
        areas_list = AREAS.get(city, ['all neighborhoods'])
    else:
        areas_list = ['all areas']
    areas_str = ', '.join(areas_list)
    
    sections = [
        generate_intro(primary_kw, location, lsi_keywords),
        generate_why_location(primary_kw, location, lsi_keywords),
        generate_benefits(primary_kw, location),
        generate_services(primary_kw, location),
        generate_faqs(primary_kw, location, areas_str),
        generate_success_story(primary_kw, location),
        generate_cta(primary_kw, location)
    ]
    
    # Shuffle middle sections for variety
    middle = sections[1:-1]
    random.shuffle(middle)
    sections = [sections[0]] + middle + [sections[-1]]
    
    body_content = "\n\n".join(sections)
    
    related = generate_related_posts(f"{slugify(primary_kw)}-{slugify(location)}.html")
    if related:
        body_content += "\n\n" + related
    
    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_description}">
    <meta name="keywords" content="{primary_kw}, {location}, {', '.join(lsi_keywords[:10]) if lsi_keywords else primary_kw}, SIDDHI AI, digital agency, web development, SEO, Python training">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_description}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{SITE_URL}/blog/posts/{slugify(primary_kw)}-{slugify(location)}.html">
    <meta property="og:image" content="{SITE_URL}/assets/blog-default.jpg">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{SITE_URL}/blog/posts/{slugify(primary_kw)}-{slugify(location)}.html">
    
    <!-- Tailwind & Lucide -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200;300;400;600;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-rgb: 2, 2, 3;
            --accent-rgb: 229, 183, 105;
            --tech-rgb: 0, 240, 255;
            --text-rgb: 229, 231, 235;
            --text-muted-rgb: 156, 163, 175;
            --card-bg: rgba(8, 8, 10, 0.75);
        }}
        [data-theme="rich"] {{
            --bg-rgb: 26, 11, 46;
            --accent-rgb: 212, 175, 55;
            --tech-rgb: 255, 42, 109;
            --text-rgb: 243, 232, 255;
            --text-muted-rgb: 216, 180, 226;
            --card-bg: rgba(26, 11, 46, 0.75);
        }}
        [data-theme="sunny"] {{
            --bg-rgb: 224, 242, 254;
            --accent-rgb: 245, 158, 11;
            --tech-rgb: 2, 132, 199;
            --text-rgb: 15, 23, 42;
            --text-muted-rgb: 71, 85, 105;
            --card-bg: rgba(255, 255, 255, 0.6);
        }}
        body {{
            background-color: rgb(var(--bg-rgb));
            color: rgb(var(--text-rgb));
            font-family: 'Plus Jakarta Sans', sans-serif;
            transition: background-color 0.5s ease, color 0.5s ease;
        }}
        .glass-panel {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(var(--accent-rgb), 0.3);
        }}
        .gold-gradient {{
            background: linear-gradient(135deg, rgb(var(--accent-rgb)) 0%, #FFF8DC 50%, rgb(var(--accent-rgb)) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .rgb-card {{
            position: relative;
            background: rgb(var(--bg-rgb));
            border-radius: 1.5rem;
            overflow: hidden;
        }}
        .rgb-card::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(rgb(var(--tech-rgb)), rgb(var(--accent-rgb)), #FF0055, #9D00FF, rgb(var(--tech-rgb)));
            animation: rgbSpin 4s linear infinite;
            opacity: 0.3;
        }}
        .rgb-card:hover::before {{
            opacity: 1;
        }}
        .rgb-content {{
            position: absolute;
            inset: 2px;
            background: var(--card-bg);
            border-radius: calc(1.5rem - 2px);
            z-index: 10;
            padding: 1.5rem;
        }}
        @keyframes rgbSpin {{
            100% {{ transform: rotate(360deg); }}
        }}
        .btn-creepy {{
            position: relative;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .btn-creepy .eyes-wrapper {{
            position: absolute;
            right: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            gap: 4px;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }}
        .btn-creepy:hover .eyes-wrapper {{
            opacity: 1;
        }}
        .btn-creepy:hover .btn-text-content {{
            transform: translateX(-15px);
        }}
        .creepy-eye {{
            width: 14px;
            height: 14px;
            background: #fff;
            border-radius: 50%;
            position: relative;
        }}
        .creepy-pupil {{
            width: 6px;
            height: 6px;
            background: #000;
            border-radius: 50%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }}
        .blog-content h2 {{
            font-size: 2rem;
            font-family: 'Playfair Display', serif;
            margin: 2.5rem 0 1.5rem;
            color: rgb(var(--text-rgb));
        }}
        .blog-content h3 {{
            font-size: 1.25rem;
            font-weight: 700;
            margin: 1.5rem 0 1rem;
            color: rgb(var(--accent-rgb));
        }}
        .blog-content p {{
            line-height: 1.8;
            color: rgb(var(--text-muted-rgb));
            margin-bottom: 1.5rem;
        }}
        .blog-content ul {{
            list-style: none;
            padding-left: 0;
            margin: 1.5rem 0;
        }}
        .blog-content li {{
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(var(--text-muted-rgb), 0.1);
        }}
    </style>
    
    <script>
        function changeTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
        }}
    </script>
</head>
<body class="min-h-screen">
    <!-- Simple nav for blog posts -->
    <nav class="fixed w-full z-50 backdrop-blur-md border-b border-textmain/10 bg-obsidian/40">
        <div class="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
            <a href="{SITE_URL}" class="font-extrabold text-xl">SIDDHI <span class="text-accent">AI</span></a>
            <div class="flex items-center gap-4">
                <a href="{SITE_URL}/blog" class="text-[10px] uppercase tracking-widest hover:text-accent">← Back to Blog</a>
                <div class="flex gap-2">
                    <button onclick="changeTheme('dark')" class="w-4 h-4 rounded-full bg-[#020203] border border-gray-500"></button>
                    <button onclick="changeTheme('rich')" class="w-4 h-4 rounded-full bg-[#1a0b2e] border border-[#d4af37]"></button>
                    <button onclick="changeTheme('sunny')" class="w-4 h-4 rounded-full bg-[#e0f2fe] border border-[#f59e0b]"></button>
                </div>
            </div>
        </div>
    </nav>

    <main class="pt-24 pb-16">
        <article class="max-w-4xl mx-auto px-6">
            <header class="text-center mb-12">
                <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/10 mb-6">
                    <span class="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
                    <span class="text-[9px] font-bold text-accent uppercase tracking-widest">{location}</span>
                </div>
                <h1 class="font-serif text-5xl md:text-6xl text-textmain mb-4">{title}</h1>
                <div class="flex items-center justify-center gap-4 text-textmuted text-sm">
                    <span>Published on {current_date}</span>
                    <span>•</span>
                    <span>By SIDDHI AI Team</span>
                </div>
            </header>
            
            <div class="blog-content glass-panel rounded-[2rem] p-8 md:p-12">
                {body_content}
            </div>
        </article>
    </main>

    <footer class="py-8 border-t border-textmain/10 bg-obsidian text-center">
        <p class="text-[9px] text-textmuted uppercase tracking-widest">&copy; 2017-{year} SIDDHI AI. All rights reserved.</p>
    </footer>

    <script>
        lucide.createIcons();
    </script>
</body>
</html>"""
    
    return html, title, meta_description

# -------------------- BLOG INDEX GENERATION --------------------
def generate_blog_index() -> str:
    posts = []
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR, exist_ok=True)
    
    for fname in sorted(os.listdir(POSTS_DIR), reverse=True):
        if not fname.endswith('.html'):
            continue
        filepath = os.path.join(POSTS_DIR, fname)
        content = safe_read_file(filepath)
        if not content:
            continue
        
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else fname.replace('.html', '').replace('-', ' ').title()
        
        desc_match = re.search(r'<meta name="description" content="([^"]+)"', content)
        description = desc_match.group(1) if desc_match else f"Read our guide on {title}"
        
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', fname)
        date = date_match.group(1) if date_match else datetime.datetime.now().strftime("%Y-%m-%d")
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            display_date = date_obj.strftime("%B %d, %Y")
        except:
            display_date = date
        
        location_match = re.search(r'in ([A-Za-z\s,]+)(?:\s*[–-]\s*\d{4}|$)', title)
        location = location_match.group(1).strip() if location_match else "Global"
        
        posts.append({
            'title': title,
            'description': description[:120] + "..." if len(description) > 120 else description,
            'date': display_date,
            'filename': fname,
            'location': location
        })
    
    cards_html = ""
    for post in posts:
        cards_html += f"""
        <div class="tilt-wrapper h-full">
            <div class="rgb-card h-full">
                <div class="rgb-content flex flex-col">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-[9px] font-bold text-accent uppercase tracking-widest">{post['location']}</span>
                        <span class="text-[9px] text-textmuted">•</span>
                        <span class="text-[9px] text-textmuted">{post['date']}</span>
                    </div>
                    <h3 class="text-xl font-bold text-textmain mb-3 line-clamp-2">{post['title']}</h3>
                    <p class="text-textmuted text-sm font-light mb-4 flex-1 line-clamp-3">{post['description']}</p>
                    <a href="/blog/posts/{post['filename']}" class="btn-creepy self-start mt-auto bg-transparent border border-accent text-accent px-6 py-2 rounded-full text-[9px] font-bold uppercase tracking-widest hover:bg-accent hover:text-obsidian transition-all">
                        <span class="btn-text-content">Read More</span>
                        <div class="eyes-wrapper">
                            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                        </div>
                    </a>
                </div>
            </div>
        </div>"""
    
    year = datetime.datetime.now().year
    
    index_html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIDDHI AI Blog - Insights & Articles</title>
    <meta name="description" content="Expert insights on Python training, digital marketing, web development, and AI solutions. SIDDHI AI's official blog with daily updates and industry trends.">
    <meta name="keywords" content="Python training blog, digital marketing tips, web development articles, AI insights, SEO guide, Madhya Pradesh, India">
    
    <meta property="og:title" content="SIDDHI AI Blog">
    <meta property="og:description" content="Expert insights on Python training, digital marketing, web development, and AI solutions.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}/blog/">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200;300;400;600;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-rgb: 2, 2, 3;
            --accent-rgb: 229, 183, 105;
            --tech-rgb: 0, 240, 255;
            --text-rgb: 229, 231, 235;
            --text-muted-rgb: 156, 163, 175;
            --card-bg: rgba(8, 8, 10, 0.75);
        }}
        [data-theme="rich"] {{
            --bg-rgb: 26, 11, 46;
            --accent-rgb: 212, 175, 55;
            --tech-rgb: 255, 42, 109;
            --text-rgb: 243, 232, 255;
            --text-muted-rgb: 216, 180, 226;
            --card-bg: rgba(26, 11, 46, 0.75);
        }}
        [data-theme="sunny"] {{
            --bg-rgb: 224, 242, 254;
            --accent-rgb: 245, 158, 11;
            --tech-rgb: 2, 132, 199;
            --text-rgb: 15, 23, 42;
            --text-muted-rgb: 71, 85, 105;
            --card-bg: rgba(255, 255, 255, 0.6);
        }}
        body {{
            background-color: rgb(var(--bg-rgb));
            color: rgb(var(--text-rgb));
            font-family: 'Plus Jakarta Sans', sans-serif;
            transition: background-color 0.5s ease, color 0.5s ease;
        }}
        .glass-panel {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(var(--accent-rgb), 0.3);
        }}
        .gold-gradient {{
            background: linear-gradient(135deg, rgb(var(--accent-rgb)) 0%, #FFF8DC 50%, rgb(var(--accent-rgb)) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .tilt-wrapper {{ perspective: 1200px; }}
        .rgb-card {{
            position: relative;
            background: rgb(var(--bg-rgb));
            border-radius: 1.5rem;
            overflow: hidden;
            height: 100%;
            min-height: 320px;
        }}
        .rgb-card::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(rgb(var(--tech-rgb)), rgb(var(--accent-rgb)), #FF0055, #9D00FF, rgb(var(--tech-rgb)));
            animation: rgbSpin 4s linear infinite;
            opacity: 0.3;
        }}
        .rgb-card:hover::before {{
            opacity: 1;
        }}
        .rgb-content {{
            position: absolute;
            inset: 2px;
            background: var(--card-bg);
            border-radius: calc(1.5rem - 2px);
            z-index: 10;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            height: calc(100% - 4px);
        }}
        @keyframes rgbSpin {{
            100% {{ transform: rotate(360deg); }}
        }}
        .btn-creepy {{
            position: relative;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .btn-creepy .eyes-wrapper {{
            position: absolute;
            right: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            gap: 4px;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }}
        .btn-creepy:hover .eyes-wrapper {{
            opacity: 1;
        }}
        .btn-creepy:hover .btn-text-content {{
            transform: translateX(-15px);
        }}
        .line-clamp-2 {{
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .line-clamp-3 {{
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
    </style>
    
    <script>
        function changeTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
        }}
    </script>
</head>
<body>
    <!-- Navigation (matches main site) -->
    <nav class="fixed w-full z-50 backdrop-blur-md border-b border-textmain/10 bg-obsidian/40">
        <div class="max-w-7xl mx-auto px-6 lg:px-12">
            <div class="flex justify-between items-center h-20">
                <a href="{SITE_URL}" class="flex items-center gap-3">
                    <i data-lucide="cpu" class="text-accent w-6 h-6"></i>
                    <span class="font-extrabold text-xl tracking-tighter">SIDDHI <span class="text-accent">AI</span></span>
                </a>
                
                <div class="hidden md:flex items-center space-x-6">
                    <a href="{SITE_URL}/#benefits" class="text-[10px] uppercase tracking-[0.2em] font-bold text-textmuted hover:text-accent">Why Us</a>
                    <a href="{SITE_URL}/#architectures" class="text-[10px] uppercase tracking-[0.2em] font-bold text-textmuted hover:text-accent">Services</a>
                    <a href="{SITE_URL}/#global-reach" class="text-[10px] uppercase tracking-[0.2em] font-bold text-textmuted hover:text-accent">Global Reach</a>
                    <a href="/blog" class="text-[10px] uppercase tracking-[0.2em] font-bold text-accent">Blog</a>
                    
                    <div class="flex items-center gap-2 ml-4 border-l border-textmuted/30 pl-6">
                        <button onclick="changeTheme('dark')" class="w-4 h-4 rounded-full bg-[#020203] border-2 border-gray-500"></button>
                        <button onclick="changeTheme('rich')" class="w-4 h-4 rounded-full bg-[#1a0b2e] border-2 border-[#d4af37]"></button>
                        <button onclick="changeTheme('sunny')" class="w-4 h-4 rounded-full bg-[#e0f2fe] border-2 border-[#f59e0b]"></button>
                    </div>
                </div>
                
                <a href="{SITE_URL}/#contact" class="hidden md:flex bg-accent text-obsidian px-6 py-2.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] btn-creepy">
                    <span class="btn-text-content">Start Project</span>
                    <div class="eyes-wrapper">
                        <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                        <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                    </div>
                </a>
            </div>
        </div>
    </nav>

    <main class="pt-32 pb-20">
        <div class="max-w-7xl mx-auto px-6">
            <!-- Header -->
            <div class="text-center max-w-3xl mx-auto mb-16">
                <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/10 mb-6">
                    <span class="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
                    <span class="text-[9px] font-bold text-accent uppercase tracking-widest">Knowledge Hub</span>
                </div>
                <h1 class="font-serif text-5xl md:text-6xl text-textmain mb-4">Blog & <span class="gold-gradient italic">Insights</span></h1>
                <p class="text-textmuted text-lg font-light">Expert articles on Python, AI, digital marketing, and web development – updated daily.</p>
            </div>
            
            <!-- Blog Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {cards_html if cards_html else '<div class="col-span-full text-center text-textmuted py-20"><p>No articles yet. Check back soon!</p></div>'}
            </div>
        </div>
    </main>

    <footer class="py-12 border-t border-textmain/10 bg-obsidian">
        <div class="max-w-7xl mx-auto px-6 text-center">
            <span class="font-extrabold text-2xl tracking-tighter text-textmain mb-6 block">SIDDHI <span class="text-accent">AI</span></span>
            <div class="flex justify-center gap-6 mb-6">
                <a href="https://github.com/CodeWander-666-github" class="text-textmuted hover:text-accent">
                    <i data-lucide="github" class="w-5 h-5"></i>
                </a>
            </div>
            <p class="text-[9px] text-textmuted uppercase tracking-widest">&copy; 2017-{year} SIDDHI AI. All rights reserved.</p>
        </div>
    </footer>

    <script>
        lucide.createIcons();
    </script>
</body>
</html>"""
    
    return index_html

# -------------------- MAIN --------------------
def main():
    logger.info("=" * 60)
    logger.info("🚀 Starting SIDDHI AI Enhanced Blog Generator")
    logger.info("=" * 60)
    
    try:
        os.makedirs(POSTS_DIR, exist_ok=True)
        
        primary_kw = random.choice(MASTER_KEYWORDS)
        location, loc_type = select_location()
        logger.info(f"📝 Primary keyword: {primary_kw}")
        logger.info(f"📍 Location: {location} ({loc_type})")
        
        html, title, meta = generate_article(primary_kw, location)
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        base_slug = slugify(f"{primary_kw}-{location}")
        filename = f"{date_str}-{base_slug}.html"
        filepath = os.path.join(POSTS_DIR, filename)
        counter = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filepath = os.path.join(POSTS_DIR, f"{name}-{counter}{ext}")
            counter += 1
        
        if safe_write_file(filepath, html):
            logger.info(f"✅ Article saved: {filepath}")
        else:
            logger.error("❌ Failed to save article")
            return
        
        index_html = generate_blog_index()
        if safe_write_file(INDEX_FILE, index_html):
            logger.info(f"✅ Blog index updated: {INDEX_FILE}")
        else:
            logger.error("❌ Failed to update blog index")
            return
        
        logger.info("🎉 Blog generation completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# -------------------- UTILITY FUNCTIONS --------------------
def slugify(text: str) -> str:
    """Convert text to URL‑friendly slug."""
    text = text.lower().replace(" ", "-")
    text = re.sub(rf"[{re.escape(punctuation)}]", "", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")

def fetch_with_retry(url: str, params: Dict = None) -> Optional[requests.Response]:
    """Fetch URL with exponential backoff retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt))
            else:
                logger.error(f"All retries failed for URL: {url}")
                return None

def get_lsi_keywords(phrase: str, max_results: int = 5) -> List[str]:
    """Fetch semantically related keywords from Datamuse API."""
    try:
        params = {'ml': phrase, 'max': max_results}
        response = fetch_with_retry(DATAMUSE_API, params=params)
        if response and response.status_code == 200:
            data = response.json()
            keywords = [item['word'] for item in data if 'word' in item]
            logger.info(f"Found {len(keywords)} LSI keywords for '{phrase}'")
            return keywords
    except Exception as e:
        logger.error(f"Error fetching LSI keywords: {e}")
    return []

def safe_read_file(filepath: str) -> Optional[str]:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return None

def safe_write_file(filepath: str, content: str) -> bool:
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully wrote file: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error writing file {filepath}: {e}")
        return False

# -------------------- KEYWORD EXTRACTION FROM INDEX.HTML --------------------
def extract_keywords_from_index() -> List[str]:
    """Parse the hidden SEO keywords div from index.html and return a list of unique keywords."""
    content = safe_read_file(INDEX_HTML_PATH)
    if not content:
        logger.warning("Could not read index.html; using default keywords.")
        return []
    
    # Find the hidden div with keywords
    pattern = r'<div style="display:none;">(.*?)</div>'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        logger.warning("No hidden keywords div found in index.html.")
        return []
    
    keywords_text = match.group(1)
    # Split by commas and clean
    keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    logger.info(f"Extracted {len(unique_keywords)} unique keywords from index.html")
    return unique_keywords

# Global keyword list (loaded once)
MASTER_KEYWORDS = extract_keywords_from_index() or [
    "learn python for beginners", "digital marketing agency in india", "web development",
    "SEO services", "AI solutions", "stock market analysis", "Python training"
]

# -------------------- LOCATION SELECTION (same as before) --------------------
GLOBAL_LOCATIONS = ["United States", "Canada", "United Kingdom", "Australia", "New Zealand", "Ireland"]
COUNTRY = "India"
STATES = {
    "Madhya Pradesh": ["Indore", "Bhopal", "Gwalior", "Jabalpur", "Ujjain"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"]
}
AREAS = {
    "Indore": ["Vijay Nagar", "New Palasia", "Scheme No. 78", "Rajendra Nagar", "Bholaram"],
    "Bangalore": ["Indiranagar", "Whitefield", "Koramangala", "HSR Layout", "Jayanagar"]
}

def select_location() -> Tuple[str, str]:
    levels = ['global', 'country', 'state', 'city', 'area']
    weights = [0.1, 0.2, 0.2, 0.3, 0.2]
    level = random.choices(levels, weights=weights)[0]
    if level == 'global':
        return random.choice(GLOBAL_LOCATIONS), "global"
    elif level == 'country':
        return COUNTRY, "country"
    elif level == 'state':
        state = random.choice(list(STATES.keys()))
        return state, "state"
    elif level == 'city':
        state = random.choice(list(STATES.keys()))
        city = random.choice(STATES[state])
        return f"{city}, {state}", "city"
    else:
        city = random.choice(list(AREAS.keys()))
        area = random.choice(AREAS[city])
        return f"{area}, {city}", "area"

# -------------------- CONTENT GENERATION MODULES --------------------
def generate_intro(primary_kw: str, location: str, lsi_keywords: List[str]) -> str:
    lsi_phrase = ", ".join(lsi_keywords[:3]) if lsi_keywords else primary_kw
    return f"""<p>Are you searching for the best <strong>{primary_kw} in {location}</strong>? You've come to the right place. At <strong>SIDDHI AI</strong>, we specialize in delivering world-class {primary_kw} services tailored to businesses and individuals in {location}. With our proven track record and cutting-edge technology, we've helped hundreds of clients achieve their digital goals.</p>

<p>In this comprehensive guide, we'll explore everything you need to know about {primary_kw} in {location}, including local trends, pricing, expert tips, and how SIDDHI AI can help you succeed in {datetime.datetime.now().year}.</p>"""

def generate_why_location(primary_kw: str, location: str, lsi_keywords: List[str]) -> str:
    lsi_phrase = ", ".join(lsi_keywords[:3]) if lsi_keywords else primary_kw
    return f"""<h2>Why {location} is a Prime Destination for {primary_kw.title()}</h2>
<p>{location} has emerged as a thriving hub for digital innovation and business growth. With a rapidly expanding economy and increasing demand for professional {primary_kw.lower()} services, now is the ideal time to invest in {primary_kw}. Local businesses in {location} are leveraging {lsi_phrase} to gain competitive advantages and reach wider audiences.</p>

<p>SIDDHI AI understands the unique dynamics of the {location} market. Our team combines global expertise with local insights to deliver solutions that resonate with your target audience. Whether you're a startup, SME, or enterprise, we have the right strategy for you.</p>"""

def generate_benefits(primary_kw: str, location: str) -> str:
    benefits_list = [
        f"<strong>✓ Local Market Expertise:</strong> We understand {location}'s business landscape and consumer behavior.",
        f"<strong>✓ Customized Solutions:</strong> Tailored {primary_kw} strategies for {location}'s unique requirements.",
        f"<strong>✓ Proven Results:</strong> Track record of successful projects across {location}.",
        f"<strong>✓ Cost-Effective:</strong> Competitive pricing without compromising on quality.",
        f"<strong>✓ Ongoing Support:</strong> 24/7 assistance from our {location}-based team.",
        f"<strong>✓ Data-Driven Approach:</strong> We use analytics to continuously optimize your campaigns.",
        f"<strong>✓ Award-Winning Team:</strong> Recognized experts in {primary_kw} and digital innovation."
    ]
    # Shuffle and pick 5-6
    selected = random.sample(benefits_list, min(6, len(benefits_list)))
    items = "".join(f"<li>{item}</li>" for item in selected)
    return f"""<h2>Key Benefits of Professional {primary_kw.title()} in {location}</h2>
<ul class="space-y-3">{items}</ul>"""

def generate_services(primary_kw: str, location: str) -> str:
    services_list = [
        f"<strong>🔹 Complete {primary_kw} Packages:</strong> End-to-end solutions for startups and enterprises.",
        f"<strong>🔹 Custom Strategy Development:</strong> Tailored approaches for your specific goals.",
        f"<strong>🔹 Implementation & Management:</strong> Full-service execution with regular updates.",
        f"<strong>🔹 Analytics & Reporting:</strong> Detailed insights into your campaign performance.",
        f"<strong>🔹 Training & Workshops:</strong> Hands-on {primary_kw} training for your team in {location}.",
        f"<strong>🔹 24/7 Support:</strong> Round-the-clock assistance from our experts."
    ]
    items = "".join(f"<li>{item}</li>" for item in services_list)
    return f"""<h2>Our {primary_kw.title()} Services in {location}</h2>
<p>SIDDHI AI offers comprehensive {primary_kw} solutions designed for businesses in {location}:</p>
<ul class="space-y-2">{items}</ul>"""

def generate_faqs(primary_kw: str, location: str, areas_str: str) -> str:
    faqs = [
        (f"❓ How much does {primary_kw} cost in {location}?",
         f"Prices vary based on project scope and requirements. Contact SIDDHI AI for a free, no-obligation quote tailored to your needs."),
        (f"❓ Why choose SIDDHI AI for {primary_kw} in {location}?",
         f"SIDDHI AI combines international standards with local expertise. We're verified (GST & Udyam), have 66+ global clients, and offer 24/7 support from our {location} team."),
        (f"❓ How quickly can I see results?",
         f"Timelines depend on the specific service. Typically, clients see initial improvements within 2-3 months of starting our {primary_kw} services."),
        (f"❓ Do you serve specific areas within {location}?",
         f"Yes! We serve all areas including {areas_str}."),
        (f"❓ What industries do you specialize in?",
         f"We work with a wide range of industries including e-commerce, healthcare, education, real estate, and technology."),
        (f"❓ Can I get a customized package?",
         f"Absolutely! We tailor our services to meet your unique business needs and budget.")
    ]
    # Select 4-5 random FAQs
    selected = random.sample(faqs, min(5, len(faqs)))
    faq_html = ""
    for q, a in selected:
        faq_html += f"""
    <div>
        <h3>{q}</h3>
        <p>{a}</p>
    </div>"""
    return f"""<h2>Frequently Asked Questions About {primary_kw} in {location}</h2>
<div class="space-y-6">{faq_html}</div>"""

def generate_success_story(primary_kw: str, location: str) -> str:
    stories = [
        (f"Startup in {location}", f"increased their website traffic by 200% and doubled sales within 6 months using our {primary_kw} services."),
        (f"Local e‑commerce store", f"achieved a 150% boost in conversions after implementing our {primary_kw} strategies."),
        (f"Educational institution", f"saw a 300% increase in course enrollments through targeted {primary_kw} campaigns."),
        (f"Real estate agency", f"generated 80+ qualified leads per month with our {primary_kw} expertise."),
    ]
    client, result = random.choice(stories)
    return f"""<h2>Success Story: {client}</h2>
<p>A {client} in {location} partnered with SIDDHI AI to transform their online presence through our {primary_kw} services. Within months, they {result}</p>"""

def generate_cta(primary_kw: str, location: str) -> str:
    return f"""<div class="text-center my-12">
    <p class="text-lg mb-6">Ready to dominate {primary_kw} in {location}? Let's talk!</p>
    <a href="/#contact" class="btn-creepy inline-flex bg-accent text-obsidian px-8 py-4 rounded-full text-[10px] font-black uppercase tracking-[0.2em] transition-all hover:bg-textmain shadow-[0_0_20px_rgba(var(--accent-rgb),0.2)]">
        <span class="btn-text-content">Free Consultation</span>
        <div class="eyes-wrapper">
            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
        </div>
    </a>
</div>"""

def generate_related_posts(current_post_filename: str) -> str:
    """Generate a list of links to other blog posts (excluding current)."""
    posts = []
    if os.path.exists(POSTS_DIR):
        all_posts = [f for f in os.listdir(POSTS_DIR) if f.endswith('.html') and f != current_post_filename]
        # Pick up to 3 random posts
        selected = random.sample(all_posts, min(3, len(all_posts)))
        for fname in selected:
            # Extract title from file (simple)
            content = safe_read_file(os.path.join(POSTS_DIR, fname))
            if content:
                title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
                title = title_match.group(1).strip() if title_match else fname.replace('.html', '').replace('-', ' ').title()
                posts.append((title, f"/blog/posts/{fname}"))
    if not posts:
        return ""
    
    links = "".join(f'<li><a href="{url}" class="hover:text-accent transition-colors">{title}</a></li>' for title, url in posts)
    return f"""
<div class="mt-16 pt-8 border-t border-textmain/10">
    <h3 class="text-2xl font-serif mb-6">Related Articles</h3>
    <ul class="space-y-2">{links}</ul>
</div>"""

# -------------------- ARTICLE GENERATION (MAIN) --------------------
def generate_article(primary_kw: str, location: str) -> Tuple[str, str, str]:
    year = datetime.datetime.now().year
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    # Title variations
    title_templates = [
        f"Best {primary_kw} in {location} – {year} Complete Guide",
        f"Top {primary_kw} Services in {location}: {year} Review",
        f"How to Choose the Right {primary_kw} in {location} ({year})",
        f"{primary_kw} in {location}: Expert Tips & Strategies for {year}",
        f"The Ultimate Guide to {primary_kw} in {location} ({year})"
    ]
    title = random.choice(title_templates)
    
    meta_description = f"Looking for expert {primary_kw} in {location}? SIDDHI AI provides top-rated {primary_kw.lower()} solutions. Free consultation! ⭐⭐⭐⭐⭐"
    
    # Get LSI keywords for content enrichment
    lsi_keywords = get_lsi_keywords(f"{primary_kw} {location}")
    
    # Pre‑compute areas for FAQ
    if ',' in location:
        city = location.split(',')[0].strip()
        areas_list = AREAS.get(city, ['all neighborhoods'])
    else:
        areas_list = ['all areas']
    areas_str = ', '.join(areas_list)
    
    # Build content sections (order may vary)
    sections = [
        generate_intro(primary_kw, location, lsi_keywords),
        generate_why_location(primary_kw, location, lsi_keywords),
        generate_benefits(primary_kw, location),
        generate_services(primary_kw, location),
        generate_faqs(primary_kw, location, areas_str),
        generate_success_story(primary_kw, location),
        generate_cta(primary_kw, location)
    ]
    
    # Possibly shuffle sections except intro and cta
    # Keep intro first, cta last, shuffle the middle
    middle = sections[1:-1]
    random.shuffle(middle)
    sections = [sections[0]] + middle + [sections[-1]]
    
    body_content = "\n\n".join(sections)
    
    # Add related posts after the article
    related = generate_related_posts(f"{slugify(primary_kw)}-{slugify(location)}.html")
    if related:
        body_content += "\n\n" + related
    
    # Complete HTML template (same as before, but with the new body)
    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_description}">
    <meta name="keywords" content="{primary_kw}, {location}, {', '.join(lsi_keywords[:10]) if lsi_keywords else primary_kw}, SIDDHI AI, digital agency, web development, SEO, Python training">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_description}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{SITE_URL}/blog/posts/{slugify(primary_kw)}-{slugify(location)}.html">
    <meta property="og:image" content="{SITE_URL}/assets/blog-default.jpg">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{SITE_URL}/blog/posts/{slugify(primary_kw)}-{slugify(location)}.html">
    
    <!-- Tailwind & Lucide -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200;300;400;600;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-rgb: 2, 2, 3;
            --accent-rgb: 229, 183, 105;
            --tech-rgb: 0, 240, 255;
            --text-rgb: 229, 231, 235;
            --text-muted-rgb: 156, 163, 175;
            --card-bg: rgba(8, 8, 10, 0.75);
        }}
        [data-theme="rich"] {{
            --bg-rgb: 26, 11, 46;
            --accent-rgb: 212, 175, 55;
            --tech-rgb: 255, 42, 109;
            --text-rgb: 243, 232, 255;
            --text-muted-rgb: 216, 180, 226;
            --card-bg: rgba(26, 11, 46, 0.75);
        }}
        [data-theme="sunny"] {{
            --bg-rgb: 224, 242, 254;
            --accent-rgb: 245, 158, 11;
            --tech-rgb: 2, 132, 199;
            --text-rgb: 15, 23, 42;
            --text-muted-rgb: 71, 85, 105;
            --card-bg: rgba(255, 255, 255, 0.6);
        }}
        body {{
            background-color: rgb(var(--bg-rgb));
            color: rgb(var(--text-rgb));
            font-family: 'Plus Jakarta Sans', sans-serif;
            transition: background-color 0.5s ease, color 0.5s ease;
        }}
        .glass-panel {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(var(--accent-rgb), 0.3);
        }}
        .gold-gradient {{
            background: linear-gradient(135deg, rgb(var(--accent-rgb)) 0%, #FFF8DC 50%, rgb(var(--accent-rgb)) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .rgb-card {{
            position: relative;
            background: rgb(var(--bg-rgb));
            border-radius: 1.5rem;
            overflow: hidden;
        }}
        .rgb-card::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(rgb(var(--tech-rgb)), rgb(var(--accent-rgb)), #FF0055, #9D00FF, rgb(var(--tech-rgb)));
            animation: rgbSpin 4s linear infinite;
            opacity: 0.3;
        }}
        .rgb-card:hover::before {{
            opacity: 1;
        }}
        .rgb-content {{
            position: absolute;
            inset: 2px;
            background: var(--card-bg);
            border-radius: calc(1.5rem - 2px);
            z-index: 10;
            padding: 1.5rem;
        }}
        @keyframes rgbSpin {{
            100% {{ transform: rotate(360deg); }}
        }}
        .btn-creepy {{
            position: relative;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .btn-creepy .eyes-wrapper {{
            position: absolute;
            right: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            gap: 4px;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }}
        .btn-creepy:hover .eyes-wrapper {{
            opacity: 1;
        }}
        .btn-creepy:hover .btn-text-content {{
            transform: translateX(-15px);
        }}
        .creepy-eye {{
            width: 14px;
            height: 14px;
            background: #fff;
            border-radius: 50%;
            position: relative;
        }}
        .creepy-pupil {{
            width: 6px;
            height: 6px;
            background: #000;
            border-radius: 50%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }}
        .blog-content h2 {{
            font-size: 2rem;
            font-family: 'Playfair Display', serif;
            margin: 2.5rem 0 1.5rem;
            color: rgb(var(--text-rgb));
        }}
        .blog-content h3 {{
            font-size: 1.25rem;
            font-weight: 700;
            margin: 1.5rem 0 1rem;
            color: rgb(var(--accent-rgb));
        }}
        .blog-content p {{
            line-height: 1.8;
            color: rgb(var(--text-muted-rgb));
            margin-bottom: 1.5rem;
        }}
        .blog-content ul {{
            list-style: none;
            padding-left: 0;
            margin: 1.5rem 0;
        }}
        .blog-content li {{
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(var(--text-muted-rgb), 0.1);
        }}
    </style>
    
    <script>
        function changeTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
        }}
    </script>
</head>
<body class="min-h-screen">
    <!-- Simple nav for blog posts -->
    <nav class="fixed w-full z-50 backdrop-blur-md border-b border-textmain/10 bg-obsidian/40">
        <div class="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
            <a href="{SITE_URL}" class="font-extrabold text-xl">SIDDHI <span class="text-accent">AI</span></a>
            <div class="flex items-center gap-4">
                <a href="{SITE_URL}/blog" class="text-[10px] uppercase tracking-widest hover:text-accent">← Back to Blog</a>
                <div class="flex gap-2">
                    <button onclick="changeTheme('dark')" class="w-4 h-4 rounded-full bg-[#020203] border border-gray-500"></button>
                    <button onclick="changeTheme('rich')" class="w-4 h-4 rounded-full bg-[#1a0b2e] border border-[#d4af37]"></button>
                    <button onclick="changeTheme('sunny')" class="w-4 h-4 rounded-full bg-[#e0f2fe] border border-[#f59e0b]"></button>
                </div>
            </div>
        </div>
    </nav>

    <main class="pt-24 pb-16">
        <article class="max-w-4xl mx-auto px-6">
            <header class="text-center mb-12">
                <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/10 mb-6">
                    <span class="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
                    <span class="text-[9px] font-bold text-accent uppercase tracking-widest">{location}</span>
                </div>
                <h1 class="font-serif text-5xl md:text-6xl text-textmain mb-4">{title}</h1>
                <div class="flex items-center justify-center gap-4 text-textmuted text-sm">
                    <span>Published on {current_date}</span>
                    <span>•</span>
                    <span>By SIDDHI AI Team</span>
                </div>
            </header>
            
            <div class="blog-content glass-panel rounded-[2rem] p-8 md:p-12">
                {body_content}
            </div>
        </article>
    </main>

    <footer class="py-8 border-t border-textmain/10 bg-obsidian text-center">
        <p class="text-[9px] text-textmuted uppercase tracking-widest">&copy; 2017-{year} SIDDHI AI. All rights reserved.</p>
    </footer>

    <script>
        lucide.createIcons();
    </script>
</body>
</html>"""
    
    return html, title, meta_description

# -------------------- BLOG INDEX GENERATION (unchanged but uses absolute paths) --------------------
def generate_blog_index() -> str:
    posts = []
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR, exist_ok=True)
    
    for fname in sorted(os.listdir(POSTS_DIR), reverse=True):
        if not fname.endswith('.html'):
            continue
        filepath = os.path.join(POSTS_DIR, fname)
        content = safe_read_file(filepath)
        if not content:
            continue
        
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else fname.replace('.html', '').replace('-', ' ').title()
        
        desc_match = re.search(r'<meta name="description" content="([^"]+)"', content)
        description = desc_match.group(1) if desc_match else f"Read our guide on {title}"
        
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', fname)
        date = date_match.group(1) if date_match else datetime.datetime.now().strftime("%Y-%m-%d")
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            display_date = date_obj.strftime("%B %d, %Y")
        except:
            display_date = date
        
        location_match = re.search(r'in ([A-Za-z\s,]+)(?:\s*[–-]\s*\d{4}|$)', title)
        location = location_match.group(1).strip() if location_match else "Global"
        
        posts.append({
            'title': title,
            'description': description[:120] + "..." if len(description) > 120 else description,
            'date': display_date,
            'filename': fname,
            'location': location
        })
    
    cards_html = ""
    for post in posts:
        cards_html += f"""
        <div class="tilt-wrapper h-full">
            <div class="rgb-card h-full">
                <div class="rgb-content flex flex-col">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-[9px] font-bold text-accent uppercase tracking-widest">{post['location']}</span>
                        <span class="text-[9px] text-textmuted">•</span>
                        <span class="text-[9px] text-textmuted">{post['date']}</span>
                    </div>
                    <h3 class="text-xl font-bold text-textmain mb-3 line-clamp-2">{post['title']}</h3>
                    <p class="text-textmuted text-sm font-light mb-4 flex-1 line-clamp-3">{post['description']}</p>
                    <a href="/blog/posts/{post['filename']}" class="btn-creepy self-start mt-auto bg-transparent border border-accent text-accent px-6 py-2 rounded-full text-[9px] font-bold uppercase tracking-widest hover:bg-accent hover:text-obsidian transition-all">
                        <span class="btn-text-content">Read More</span>
                        <div class="eyes-wrapper">
                            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                        </div>
                    </a>
                </div>
            </div>
        </div>"""
    
    year = datetime.datetime.now().year
    
    index_html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIDDHI AI Blog - Insights & Articles</title>
    <meta name="description" content="Expert insights on Python training, digital marketing, web development, and AI solutions. SIDDHI AI's official blog with daily updates and industry trends.">
    <meta name="keywords" content="Python training blog, digital marketing tips, web development articles, AI insights, SEO guide, Madhya Pradesh, India">
    
    <meta property="og:title" content="SIDDHI AI Blog">
    <meta property="og:description" content="Expert insights on Python training, digital marketing, web development, and AI solutions.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}/blog/">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200;300;400;600;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-rgb: 2, 2, 3;
            --accent-rgb: 229, 183, 105;
            --tech-rgb: 0, 240, 255;
            --text-rgb: 229, 231, 235;
            --text-muted-rgb: 156, 163, 175;
            --card-bg: rgba(8, 8, 10, 0.75);
        }}
        [data-theme="rich"] {{
            --bg-rgb: 26, 11, 46;
            --accent-rgb: 212, 175, 55;
            --tech-rgb: 255, 42, 109;
            --text-rgb: 243, 232, 255;
            --text-muted-rgb: 216, 180, 226;
            --card-bg: rgba(26, 11, 46, 0.75);
        }}
        [data-theme="sunny"] {{
            --bg-rgb: 224, 242, 254;
            --accent-rgb: 245, 158, 11;
            --tech-rgb: 2, 132, 199;
            --text-rgb: 15, 23, 42;
            --text-muted-rgb: 71, 85, 105;
            --card-bg: rgba(255, 255, 255, 0.6);
        }}
        body {{
            background-color: rgb(var(--bg-rgb));
            color: rgb(var(--text-rgb));
            font-family: 'Plus Jakarta Sans', sans-serif;
            transition: background-color 0.5s ease, color 0.5s ease;
        }}
        .glass-panel {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(var(--accent-rgb), 0.3);
        }}
        .gold-gradient {{
            background: linear-gradient(135deg, rgb(var(--accent-rgb)) 0%, #FFF8DC 50%, rgb(var(--accent-rgb)) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .tilt-wrapper {{ perspective: 1200px; }}
        .rgb-card {{
            position: relative;
            background: rgb(var(--bg-rgb));
            border-radius: 1.5rem;
            overflow: hidden;
            height: 100%;
            min-height: 320px;
        }}
        .rgb-card::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(rgb(var(--tech-rgb)), rgb(var(--accent-rgb)), #FF0055, #9D00FF, rgb(var(--tech-rgb)));
            animation: rgbSpin 4s linear infinite;
            opacity: 0.3;
        }}
        .rgb-card:hover::before {{
            opacity: 1;
        }}
        .rgb-content {{
            position: absolute;
            inset: 2px;
            background: var(--card-bg);
            border-radius: calc(1.5rem - 2px);
            z-index: 10;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            height: calc(100% - 4px);
        }}
        @keyframes rgbSpin {{
            100% {{ transform: rotate(360deg); }}
        }}
        .btn-creepy {{
            position: relative;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .btn-creepy .eyes-wrapper {{
            position: absolute;
            right: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            gap: 4px;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }}
        .btn-creepy:hover .eyes-wrapper {{
            opacity: 1;
        }}
        .btn-creepy:hover .btn-text-content {{
            transform: translateX(-15px);
        }}
        .line-clamp-2 {{
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .line-clamp-3 {{
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
    </style>
    
    <script>
        function changeTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
        }}
    </script>
</head>
<body>
    <!-- Navigation (matches main site) -->
    <nav class="fixed w-full z-50 backdrop-blur-md border-b border-textmain/10 bg-obsidian/40">
        <div class="max-w-7xl mx-auto px-6 lg:px-12">
            <div class="flex justify-between items-center h-20">
                <a href="{SITE_URL}" class="flex items-center gap-3">
                    <i data-lucide="cpu" class="text-accent w-6 h-6"></i>
                    <span class="font-extrabold text-xl tracking-tighter">SIDDHI <span class="text-accent">AI</span></span>
                </a>
                
                <div class="hidden md:flex items-center space-x-6">
                    <a href="{SITE_URL}/#benefits" class="text-[10px] uppercase tracking-[0.2em] font-bold text-textmuted hover:text-accent">Why Us</a>
                    <a href="{SITE_URL}/#architectures" class="text-[10px] uppercase tracking-[0.2em] font-bold text-textmuted hover:text-accent">Services</a>
                    <a href="{SITE_URL}/#global-reach" class="text-[10px] uppercase tracking-[0.2em] font-bold text-textmuted hover:text-accent">Global Reach</a>
                    <a href="/blog" class="text-[10px] uppercase tracking-[0.2em] font-bold text-accent">Blog</a>
                    
                    <div class="flex items-center gap-2 ml-4 border-l border-textmuted/30 pl-6">
                        <button onclick="changeTheme('dark')" class="w-4 h-4 rounded-full bg-[#020203] border-2 border-gray-500"></button>
                        <button onclick="changeTheme('rich')" class="w-4 h-4 rounded-full bg-[#1a0b2e] border-2 border-[#d4af37]"></button>
                        <button onclick="changeTheme('sunny')" class="w-4 h-4 rounded-full bg-[#e0f2fe] border-2 border-[#f59e0b]"></button>
                    </div>
                </div>
                
                <a href="{SITE_URL}/#contact" class="hidden md:flex bg-accent text-obsidian px-6 py-2.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] btn-creepy">
                    <span class="btn-text-content">Start Project</span>
                    <div class="eyes-wrapper">
                        <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                        <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                    </div>
                </a>
            </div>
        </div>
    </nav>

    <main class="pt-32 pb-20">
        <div class="max-w-7xl mx-auto px-6">
            <!-- Header -->
            <div class="text-center max-w-3xl mx-auto mb-16">
                <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/10 mb-6">
                    <span class="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
                    <span class="text-[9px] font-bold text-accent uppercase tracking-widest">Knowledge Hub</span>
                </div>
                <h1 class="font-serif text-5xl md:text-6xl text-textmain mb-4">Blog & <span class="gold-gradient italic">Insights</span></h1>
                <p class="text-textmuted text-lg font-light">Expert articles on Python, AI, digital marketing, and web development – updated daily.</p>
            </div>
            
            <!-- Blog Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {cards_html if cards_html else '<div class="col-span-full text-center text-textmuted py-20"><p>No articles yet. Check back soon!</p></div>'}
            </div>
        </div>
    </main>

    <footer class="py-12 border-t border-textmain/10 bg-obsidian">
        <div class="max-w-7xl mx-auto px-6 text-center">
            <span class="font-extrabold text-2xl tracking-tighter text-textmain mb-6 block">SIDDHI <span class="text-accent">AI</span></span>
            <div class="flex justify-center gap-6 mb-6">
                <a href="https://github.com/CodeWander-666-github" class="text-textmuted hover:text-accent">
                    <i data-lucide="github" class="w-5 h-5"></i>
                </a>
            </div>
            <p class="text-[9px] text-textmuted uppercase tracking-widest">&copy; 2017-{year} SIDDHI AI. All rights reserved.</p>
        </div>
    </footer>

    <script>
        lucide.createIcons();
    </script>
</body>
</html>"""
    
    return index_html

# -------------------- MAIN --------------------
def main():
    logger.info("=" * 60)
    logger.info("🚀 Starting SIDDHI AI Enhanced Blog Generator")
    logger.info("=" * 60)
    
    try:
        os.makedirs(POSTS_DIR, exist_ok=True)
        
        # Select a primary keyword from the master list
        primary_kw = random.choice(MASTER_KEYWORDS)
        location, loc_type = select_location()
        logger.info(f"📝 Primary keyword: {primary_kw}")
        logger.info(f"📍 Location: {location} ({loc_type})")
        
        html, title, meta = generate_article(primary_kw, location)
        
        # Unique filename
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        base_slug = slugify(f"{primary_kw}-{location}")
        filename = f"{date_str}-{base_slug}.html"
        filepath = os.path.join(POSTS_DIR, filename)
        counter = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filepath = os.path.join(POSTS_DIR, f"{name}-{counter}{ext}")
            counter += 1
        
        if safe_write_file(filepath, html):
            logger.info(f"✅ Article saved: {filepath}")
        else:
            logger.error("❌ Failed to save article")
            return
        
        index_html = generate_blog_index()
        if safe_write_file(INDEX_FILE, index_html):
            logger.info(f"✅ Blog index updated: {INDEX_FILE}")
        else:
            logger.error("❌ Failed to update blog index")
            return
        
        logger.info("🎉 Blog generation completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()GLOBAL_LOCATIONS = [
    "United States", "Canada", "United Kingdom", "Australia",
    "New Zealand", "Ireland"
]

COUNTRY = "India"

STATES = {
    "Madhya Pradesh": ["Indore", "Bhopal", "Gwalior", "Jabalpur", "Ujjain"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"]
}

# Specific areas for cities
AREAS = {
    "Indore": ["Vijay Nagar", "New Palasia", "Scheme No. 78", "Rajendra Nagar", "Bholaram"],
    "Bangalore": ["Indiranagar", "Whitefield", "Koramangala", "HSR Layout", "Jayanagar"]
}

# API endpoints
DATAMUSE_API = "https://api.datamuse.com/words"
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 2

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# -------------------- UTILITY FUNCTIONS --------------------
def slugify(text: str) -> str:
    """Convert text to a URL‑friendly slug."""
    text = text.lower().replace(" ", "-")
    text = re.sub(rf"[{re.escape(punctuation)}]", "", text)
    text = re.sub(r"-+", "-", text)          # Replace multiple hyphens
    return text.strip("-")

def fetch_with_retry(url: str, params: Dict = None, max_retries: int = MAX_RETRIES) -> Optional[requests.Response]:
    """Fetch URL with exponential backoff retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY * (2 ** attempt))
            else:
                logger.error(f"All retries failed for URL: {url}")
                return None

def get_lsi_keywords(phrase: str, max_results: int = 5) -> List[str]:
    """Fetch semantically related keywords from Datamuse API."""
    try:
        params = {'ml': phrase, 'max': max_results}
        response = fetch_with_retry(DATAMUSE_API, params=params)
        if response and response.status_code == 200:
            data = response.json()
            keywords = [item['word'] for item in data if 'word' in item]
            logger.info(f"Found {len(keywords)} LSI keywords for '{phrase}'")
            return keywords
    except Exception as e:
        logger.error(f"Error fetching LSI keywords: {e}")
    return []

def safe_read_file(filepath: str) -> Optional[str]:
    """Safely read a file with error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return None
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        return None

def safe_write_file(filepath: str, content: str) -> bool:
    """Safely write content to a file, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully wrote file: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error writing file {filepath}: {e}")
        return False

def select_location() -> Tuple[str, str]:
    """
    Select a random location with weighted probabilities:
    - 10% global
    - 20% country (India)
    - 20% state (MP or Karnataka)
    - 30% city (Indore, Bhopal, Bangalore, etc.)
    - 20% area (specific neighbourhoods)
    Returns (location_string, location_type)
    """
    levels = ['global', 'country', 'state', 'city', 'area']
    weights = [0.1, 0.2, 0.2, 0.3, 0.2]
    level = random.choices(levels, weights=weights)[0]
    
    if level == 'global':
        return random.choice(GLOBAL_LOCATIONS), "global"
    elif level == 'country':
        return COUNTRY, "country"
    elif level == 'state':
        state = random.choice(list(STATES.keys()))
        return state, "state"
    elif level == 'city':
        state = random.choice(list(STATES.keys()))
        city = random.choice(STATES[state])
        return f"{city}, {state}", "city"
    else:  # area
        city = random.choice(list(AREAS.keys()))
        area = random.choice(AREAS[city])
        return f"{area}, {city}", "area"

# -------------------- ARTICLE GENERATION --------------------
def generate_article(topic: str, location: str) -> Tuple[str, str, str]:
    """
    Create a complete HTML article with SEO elements matching your design.
    Returns (html_content, title, meta_description)
    """
    year = datetime.datetime.now().year
    current_date = datetime.datetime.now().strftime("%B %d, %Y")
    
    title = f"Best {topic} in {location} – {year} Complete Guide"
    meta_description = f"Looking for expert {topic} services in {location}? SIDDHI AI provides top-rated {topic.lower()} solutions in {location}. Free consultation available! ⭐⭐⭐⭐⭐"
    
    lsi_keywords = get_lsi_keywords(f"{topic} {location}")
    lsi_phrase = ", ".join(lsi_keywords[:3]) if lsi_keywords else f"{topic} solutions"
    
    # --- Content sections ---
    intro = f"""<p>Are you searching for professional <strong>{topic} in {location}</strong>? You've come to the right place. At <strong>SIDDHI AI</strong>, we specialize in delivering world-class {topic} services tailored to businesses and individuals in {location}. With our proven track record and cutting-edge technology, we've helped hundreds of clients achieve their digital goals.</p>

<p>In this comprehensive guide, we'll explore everything you need to know about {topic} in {location}, including local trends, pricing, and how SIDDHI AI can help you succeed in {year}.</p>"""

    location_section = f"""<h2>Why {location} is Perfect for {topic}</h2>
<p>{location} has emerged as a thriving hub for digital innovation and business growth. With a rapidly expanding economy and increasing demand for professional {topic.lower()} services, now is the ideal time to invest in {topic}. Local businesses in {location} are leveraging {lsi_phrase} to gain competitive advantages and reach wider audiences.</p>

<p>SIDDHI AI understands the unique dynamics of the {location} market. Our team combines global expertise with local insights to deliver solutions that resonate with your target audience.</p>"""

    benefits = f"""<h2>Key Benefits of Professional {topic} in {location}</h2>
<ul class="space-y-3">
    <li><strong>✓ Local Market Expertise:</strong> We understand {location}'s business landscape and consumer behavior.</li>
    <li><strong>✓ Customized Solutions:</strong> Tailored {topic} strategies for {location}'s unique requirements.</li>
    <li><strong>✓ Proven Results:</strong> Track record of successful projects across {location}.</li>
    <li><strong>✓ Cost-Effective:</strong> Competitive pricing without compromising on quality.</li>
    <li><strong>✓ Ongoing Support:</strong> 24/7 assistance from our {location}-based team.</li>
</ul>"""

    services = f"""<h2>Our {topic} Services in {location}</h2>
<p>SIDDHI AI offers comprehensive {topic} solutions designed for businesses in {location}:</p>
<ul class="space-y-2">
    <li><strong>🔹 Complete {topic} Packages:</strong> End-to-end solutions for startups and enterprises.</li>
    <li><strong>🔹 Custom Strategy Development:</strong> Tailored approaches for your specific goals.</li>
    <li><strong>🔹 Implementation & Management:</strong> Full-service execution with regular updates.</li>
    <li><strong>🔹 Analytics & Reporting:</strong> Detailed insights into your campaign performance.</li>
    <li><strong>🔹 Training & Workshops:</strong> Hands-on {topic} training for your team in {location}.</li>
</ul>"""

    # Pre‑compute area list for FAQ to avoid nested f‑string complexity
    if ',' in location:
        city = location.split(',')[0].strip()
        areas_list = AREAS.get(city, ['all neighborhoods'])
    else:
        areas_list = ['all areas']
    areas_str = ', '.join(areas_list)

    faqs = f"""<h2>Frequently Asked Questions About {topic} in {location}</h2>
<div class="space-y-6">
    <div>
        <h3>❓ How much does {topic} cost in {location}?</h3>
        <p>Prices vary based on project scope and requirements. Contact SIDDHI AI for a free, no-obligation quote tailored to your needs.</p>
    </div>
    <div>
        <h3>❓ Why choose SIDDHI AI for {topic} in {location}?</h3>
        <p>SIDDHI AI combines international standards with local expertise. We're verified (GST & Udyam), have 66+ global clients, and offer 24/7 support from our {location} team.</p>
    </div>
    <div>
        <h3>❓ How quickly can I see results?</h3>
        <p>Timelines depend on the specific service. Typically, clients see initial improvements within 2-3 months of starting our {topic} services.</p>
    </div>
    <div>
        <h3>❓ Do you serve specific areas within {location}?</h3>
        <p>Yes! We serve all areas including {areas_str}.</p>
    </div>
</div>"""

    success = f"""<h2>Success Story: {topic} in {location}</h2>
<p>Recently, we helped a local business in {location} transform their online presence through our {topic} services. Within 6 months, they experienced:</p>
<ul class="space-y-2">
    <li>📈 200% increase in website traffic</li>
    <li>💰 150% growth in qualified leads</li>
    <li>🏆 Top 3 search rankings for key terms in {location}</li>
</ul>"""

    cta = f"""<div class="text-center my-12">
    <p class="text-lg mb-6">Ready to dominate {topic} in {location}? Let's talk!</p>
    <a href="/#contact" class="btn-creepy inline-flex bg-accent text-obsidian px-8 py-4 rounded-full text-[10px] font-black uppercase tracking-[0.2em] transition-all hover:bg-textmain shadow-[0_0_20px_rgba(var(--accent-rgb),0.2)]">
        <span class="btn-text-content">Free Consultation</span>
        <div class="eyes-wrapper">
            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
        </div>
    </a>
</div>"""

    body_content = "\n\n".join([intro, location_section, benefits, services, faqs, success, cta])

    # --- Complete HTML template (with proper escaping of curly braces) ---
    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_description}">
    <meta name="keywords" content="{topic}, {location}, {', '.join(lsi_keywords[:10]) if lsi_keywords else topic}, SIDDHI AI, digital agency, web development, SEO, Python training">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_description}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{SITE_URL}/blog/posts/{slugify(topic)}-{slugify(location)}.html">
    <meta property="og:image" content="{SITE_URL}/assets/blog-default.jpg">
    
    <!-- Canonical URL -->
    <link rel="canonical" href="{SITE_URL}/blog/posts/{slugify(topic)}-{slugify(location)}.html">
    
    <!-- Tailwind & Lucide -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200;300;400;600;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-rgb: 2, 2, 3;
            --accent-rgb: 229, 183, 105;
            --tech-rgb: 0, 240, 255;
            --text-rgb: 229, 231, 235;
            --text-muted-rgb: 156, 163, 175;
            --card-bg: rgba(8, 8, 10, 0.75);
        }}
        [data-theme="rich"] {{
            --bg-rgb: 26, 11, 46;
            --accent-rgb: 212, 175, 55;
            --tech-rgb: 255, 42, 109;
            --text-rgb: 243, 232, 255;
            --text-muted-rgb: 216, 180, 226;
            --card-bg: rgba(26, 11, 46, 0.75);
        }}
        [data-theme="sunny"] {{
            --bg-rgb: 224, 242, 254;
            --accent-rgb: 245, 158, 11;
            --tech-rgb: 2, 132, 199;
            --text-rgb: 15, 23, 42;
            --text-muted-rgb: 71, 85, 105;
            --card-bg: rgba(255, 255, 255, 0.6);
        }}
        body {{
            background-color: rgb(var(--bg-rgb));
            color: rgb(var(--text-rgb));
            font-family: 'Plus Jakarta Sans', sans-serif;
            transition: background-color 0.5s ease, color 0.5s ease;
        }}
        .glass-panel {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(var(--accent-rgb), 0.3);
        }}
        .gold-gradient {{
            background: linear-gradient(135deg, rgb(var(--accent-rgb)) 0%, #FFF8DC 50%, rgb(var(--accent-rgb)) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .rgb-card {{
            position: relative;
            background: rgb(var(--bg-rgb));
            border-radius: 1.5rem;
            overflow: hidden;
        }}
        .rgb-card::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(rgb(var(--tech-rgb)), rgb(var(--accent-rgb)), #FF0055, #9D00FF, rgb(var(--tech-rgb)));
            animation: rgbSpin 4s linear infinite;
            opacity: 0.3;
        }}
        .rgb-card:hover::before {{
            opacity: 1;
        }}
        .rgb-content {{
            position: absolute;
            inset: 2px;
            background: var(--card-bg);
            border-radius: calc(1.5rem - 2px);
            z-index: 10;
            padding: 1.5rem;
        }}
        @keyframes rgbSpin {{
            100% {{ transform: rotate(360deg); }}
        }}
        .btn-creepy {{
            position: relative;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .btn-creepy .eyes-wrapper {{
            position: absolute;
            right: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            gap: 4px;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }}
        .btn-creepy:hover .eyes-wrapper {{
            opacity: 1;
        }}
        .btn-creepy:hover .btn-text-content {{
            transform: translateX(-15px);
        }}
        .creepy-eye {{
            width: 14px;
            height: 14px;
            background: #fff;
            border-radius: 50%;
            position: relative;
        }}
        .creepy-pupil {{
            width: 6px;
            height: 6px;
            background: #000;
            border-radius: 50%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }}
        .blog-content h2 {{
            font-size: 2rem;
            font-family: 'Playfair Display', serif;
            margin: 2.5rem 0 1.5rem;
            color: rgb(var(--text-rgb));
        }}
        .blog-content h3 {{
            font-size: 1.25rem;
            font-weight: 700;
            margin: 1.5rem 0 1rem;
            color: rgb(var(--accent-rgb));
        }}
        .blog-content p {{
            line-height: 1.8;
            color: rgb(var(--text-muted-rgb));
            margin-bottom: 1.5rem;
        }}
        .blog-content ul {{
            list-style: none;
            padding-left: 0;
            margin: 1.5rem 0;
        }}
        .blog-content li {{
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(var(--text-muted-rgb), 0.1);
        }}
    </style>
    
    <script>
        function changeTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
        }}
    </script>
</head>
<body class="min-h-screen">
    <!-- Simple nav for blog posts -->
    <nav class="fixed w-full z-50 backdrop-blur-md border-b border-textmain/10 bg-obsidian/40">
        <div class="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
            <a href="{SITE_URL}" class="font-extrabold text-xl">SIDDHI <span class="text-accent">AI</span></a>
            <div class="flex items-center gap-4">
                <a href="{SITE_URL}/blog" class="text-[10px] uppercase tracking-widest hover:text-accent">← Back to Blog</a>
                <div class="flex gap-2">
                    <button onclick="changeTheme('dark')" class="w-4 h-4 rounded-full bg-[#020203] border border-gray-500"></button>
                    <button onclick="changeTheme('rich')" class="w-4 h-4 rounded-full bg-[#1a0b2e] border border-[#d4af37]"></button>
                    <button onclick="changeTheme('sunny')" class="w-4 h-4 rounded-full bg-[#e0f2fe] border border-[#f59e0b]"></button>
                </div>
            </div>
        </div>
    </nav>

    <main class="pt-24 pb-16">
        <article class="max-w-4xl mx-auto px-6">
            <header class="text-center mb-12">
                <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/10 mb-6">
                    <span class="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
                    <span class="text-[9px] font-bold text-accent uppercase tracking-widest">{location}</span>
                </div>
                <h1 class="font-serif text-5xl md:text-6xl text-textmain mb-4">{title}</h1>
                <div class="flex items-center justify-center gap-4 text-textmuted text-sm">
                    <span>Published on {current_date}</span>
                    <span>•</span>
                    <span>By SIDDHI AI Team</span>
                </div>
            </header>
            
            <div class="blog-content glass-panel rounded-[2rem] p-8 md:p-12">
                {body_content}
            </div>
        </article>
    </main>

    <footer class="py-8 border-t border-textmain/10 bg-obsidian text-center">
        <p class="text-[9px] text-textmuted uppercase tracking-widest">&copy; 2017-{year} SIDDHI AI. All rights reserved.</p>
    </footer>

    <script>
        lucide.createIcons();
    </script>
</body>
</html>"""
    
    return html, title, meta_description

# -------------------- BLOG INDEX GENERATION --------------------
def generate_blog_index() -> str:
    """
    Generate the main blog listing page with RGB cards for each post.
    Uses absolute paths (/blog/posts/filename.html) to prevent 404 errors.
    """
    posts = []
    
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR, exist_ok=True)
        logger.info(f"Created posts directory: {POSTS_DIR}")
    
    for fname in sorted(os.listdir(POSTS_DIR), reverse=True):
        if not fname.endswith('.html'):
            continue
        filepath = os.path.join(POSTS_DIR, fname)
        content = safe_read_file(filepath)
        if not content:
            continue
        
        # Extract title from <h1>
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else fname.replace('.html', '').replace('-', ' ').title()
        
        # Extract meta description
        desc_match = re.search(r'<meta name="description" content="([^"]+)"', content)
        description = desc_match.group(1) if desc_match else f"Read our guide on {title}"
        
        # Extract date from filename
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', fname)
        date = date_match.group(1) if date_match else datetime.datetime.now().strftime("%Y-%m-%d")
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            display_date = date_obj.strftime("%B %d, %Y")
        except:
            display_date = date
        
        # Extract location from title (simple heuristic)
        location_match = re.search(r'in ([A-Za-z\s,]+)(?:\s*[–-]\s*\d{4}|$)', title)
        location = location_match.group(1).strip() if location_match else "Global"
        
        posts.append({
            'title': title,
            'description': description[:120] + "..." if len(description) > 120 else description,
            'date': display_date,
            'filename': fname,
            'location': location
        })
    
    # Build RGB cards HTML
    cards_html = ""
    for post in posts:
        cards_html += f"""
        <div class="tilt-wrapper h-full">
            <div class="rgb-card h-full">
                <div class="rgb-content flex flex-col">
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-[9px] font-bold text-accent uppercase tracking-widest">{post['location']}</span>
                        <span class="text-[9px] text-textmuted">•</span>
                        <span class="text-[9px] text-textmuted">{post['date']}</span>
                    </div>
                    <h3 class="text-xl font-bold text-textmain mb-3 line-clamp-2">{post['title']}</h3>
                    <p class="text-textmuted text-sm font-light mb-4 flex-1 line-clamp-3">{post['description']}</p>
                    <a href="/blog/posts/{post['filename']}" class="btn-creepy self-start mt-auto bg-transparent border border-accent text-accent px-6 py-2 rounded-full text-[9px] font-bold uppercase tracking-widest hover:bg-accent hover:text-obsidian transition-all">
                        <span class="btn-text-content">Read More</span>
                        <div class="eyes-wrapper">
                            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                            <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                        </div>
                    </a>
                </div>
            </div>
        </div>"""
    
    year = datetime.datetime.now().year
    
    index_html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIDDHI AI Blog - Insights & Articles</title>
    <meta name="description" content="Expert insights on Python training, digital marketing, web development, and AI solutions. SIDDHI AI's official blog with daily updates and industry trends.">
    <meta name="keywords" content="Python training blog, digital marketing tips, web development articles, AI insights, SEO guide, Madhya Pradesh, India">
    
    <!-- Open Graph -->
    <meta property="og:title" content="SIDDHI AI Blog">
    <meta property="og:description" content="Expert insights on Python training, digital marketing, web development, and AI solutions.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}/blog/">
    
    <!-- Tailwind & Fonts -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200;300;400;600;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --bg-rgb: 2, 2, 3;
            --accent-rgb: 229, 183, 105;
            --tech-rgb: 0, 240, 255;
            --text-rgb: 229, 231, 235;
            --text-muted-rgb: 156, 163, 175;
            --card-bg: rgba(8, 8, 10, 0.75);
        }}
        [data-theme="rich"] {{
            --bg-rgb: 26, 11, 46;
            --accent-rgb: 212, 175, 55;
            --tech-rgb: 255, 42, 109;
            --text-rgb: 243, 232, 255;
            --text-muted-rgb: 216, 180, 226;
            --card-bg: rgba(26, 11, 46, 0.75);
        }}
        [data-theme="sunny"] {{
            --bg-rgb: 224, 242, 254;
            --accent-rgb: 245, 158, 11;
            --tech-rgb: 2, 132, 199;
            --text-rgb: 15, 23, 42;
            --text-muted-rgb: 71, 85, 105;
            --card-bg: rgba(255, 255, 255, 0.6);
        }}
        body {{
            background-color: rgb(var(--bg-rgb));
            color: rgb(var(--text-rgb));
            font-family: 'Plus Jakarta Sans', sans-serif;
            transition: background-color 0.5s ease, color 0.5s ease;
        }}
        .glass-panel {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(var(--accent-rgb), 0.3);
        }}
        .gold-gradient {{
            background: linear-gradient(135deg, rgb(var(--accent-rgb)) 0%, #FFF8DC 50%, rgb(var(--accent-rgb)) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .tilt-wrapper {{ perspective: 1200px; }}
        .rgb-card {{
            position: relative;
            background: rgb(var(--bg-rgb));
            border-radius: 1.5rem;
            overflow: hidden;
            height: 100%;
            min-height: 320px;
        }}
        .rgb-card::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: conic-gradient(rgb(var(--tech-rgb)), rgb(var(--accent-rgb)), #FF0055, #9D00FF, rgb(var(--tech-rgb)));
            animation: rgbSpin 4s linear infinite;
            opacity: 0.3;
        }}
        .rgb-card:hover::before {{
            opacity: 1;
        }}
        .rgb-content {{
            position: absolute;
            inset: 2px;
            background: var(--card-bg);
            border-radius: calc(1.5rem - 2px);
            z-index: 10;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            height: calc(100% - 4px);
        }}
        @keyframes rgbSpin {{
            100% {{ transform: rotate(360deg); }}
        }}
        .btn-creepy {{
            position: relative;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .btn-creepy .eyes-wrapper {{
            position: absolute;
            right: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            gap: 4px;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }}
        .btn-creepy:hover .eyes-wrapper {{
            opacity: 1;
        }}
        .btn-creepy:hover .btn-text-content {{
            transform: translateX(-15px);
        }}
        .line-clamp-2 {{
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        .line-clamp-3 {{
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        @media (max-width: 768px) {{
            .mobile-menu-toggle {{ display: block; }}
        }}
    </style>
    
    <script>
        function changeTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
        }}
    </script>
</head>
<body>
    <!-- Navigation (matches main site) -->
    <nav class="fixed w-full z-50 backdrop-blur-md border-b border-textmain/10 bg-obsidian/40">
        <div class="max-w-7xl mx-auto px-6 lg:px-12">
            <div class="flex justify-between items-center h-20">
                <a href="{SITE_URL}" class="flex items-center gap-3">
                    <i data-lucide="cpu" class="text-accent w-6 h-6"></i>
                    <span class="font-extrabold text-xl tracking-tighter">SIDDHI <span class="text-accent">AI</span></span>
                </a>
                
                <div class="hidden md:flex items-center space-x-6">
                    <a href="{SITE_URL}/#benefits" class="text-[10px] uppercase tracking-[0.2em] font-bold text-textmuted hover:text-accent">Why Us</a>
                    <a href="{SITE_URL}/#architectures" class="text-[10px] uppercase tracking-[0.2em] font-bold text-textmuted hover:text-accent">Services</a>
                    <a href="{SITE_URL}/#global-reach" class="text-[10px] uppercase tracking-[0.2em] font-bold text-textmuted hover:text-accent">Global Reach</a>
                    <a href="/blog" class="text-[10px] uppercase tracking-[0.2em] font-bold text-accent">Blog</a>
                    
                    <div class="flex items-center gap-2 ml-4 border-l border-textmuted/30 pl-6">
                        <button onclick="changeTheme('dark')" class="w-4 h-4 rounded-full bg-[#020203] border-2 border-gray-500"></button>
                        <button onclick="changeTheme('rich')" class="w-4 h-4 rounded-full bg-[#1a0b2e] border-2 border-[#d4af37]"></button>
                        <button onclick="changeTheme('sunny')" class="w-4 h-4 rounded-full bg-[#e0f2fe] border-2 border-[#f59e0b]"></button>
                    </div>
                </div>
                
                <a href="{SITE_URL}/#contact" class="hidden md:flex bg-accent text-obsidian px-6 py-2.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] btn-creepy">
                    <span class="btn-text-content">Start Project</span>
                    <div class="eyes-wrapper">
                        <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                        <div class="creepy-eye"><div class="creepy-pupil"></div></div>
                    </div>
                </a>
            </div>
        </div>
    </nav>

    <main class="pt-32 pb-20">
        <div class="max-w-7xl mx-auto px-6">
            <!-- Header -->
            <div class="text-center max-w-3xl mx-auto mb-16">
                <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-accent/30 bg-accent/10 mb-6">
                    <span class="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
                    <span class="text-[9px] font-bold text-accent uppercase tracking-widest">Knowledge Hub</span>
                </div>
                <h1 class="font-serif text-5xl md:text-6xl text-textmain mb-4">Blog & <span class="gold-gradient italic">Insights</span></h1>
                <p class="text-textmuted text-lg font-light">Expert articles on Python, AI, digital marketing, and web development – updated daily.</p>
            </div>
            
            <!-- Blog Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {cards_html if cards_html else '<div class="col-span-full text-center text-textmuted py-20"><p>No articles yet. Check back soon!</p></div>'}
            </div>
        </div>
    </main>

    <footer class="py-12 border-t border-textmain/10 bg-obsidian">
        <div class="max-w-7xl mx-auto px-6 text-center">
            <span class="font-extrabold text-2xl tracking-tighter text-textmain mb-6 block">SIDDHI <span class="text-accent">AI</span></span>
            <div class="flex justify-center gap-6 mb-6">
                <a href="https://github.com/CodeWander-666-github" class="text-textmuted hover:text-accent">
                    <i data-lucide="github" class="w-5 h-5"></i>
                </a>
            </div>
            <p class="text-[9px] text-textmuted uppercase tracking-widest">&copy; 2017-{year} SIDDHI AI. All rights reserved.</p>
        </div>
    </footer>

    <script>
        lucide.createIcons();
    </script>
</body>
</html>"""
    
    return index_html

# -------------------- MAIN EXECUTION --------------------
def main():
    logger.info("=" * 60)
    logger.info("🚀 Starting SIDDHI AI Blog Generator")
    logger.info("=" * 60)
    
    try:
        # Ensure posts directory exists
        os.makedirs(POSTS_DIR, exist_ok=True)
        
        # Select random topic and location
        topic = random.choice(SERVICES)
        location, loc_type = select_location()
        logger.info(f"📝 Selected topic: {topic}")
        logger.info(f"📍 Selected location: {location} ({loc_type})")
        
        # Generate article
        html, title, meta = generate_article(topic, location)
        
        # Create unique filename
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        base_slug = slugify(f"{topic}-{location}")
        filename = f"{date_str}-{base_slug}.html"
        filepath = os.path.join(POSTS_DIR, filename)
        counter = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filepath = os.path.join(POSTS_DIR, f"{name}-{counter}{ext}")
            counter += 1
            logger.info(f"File exists, trying: {os.path.basename(filepath)}")
        
        # Save article
        if safe_write_file(filepath, html):
            logger.info(f"✅ Article saved: {filepath}")
        else:
            logger.error("❌ Failed to save article")
            return
        
        # Update blog index
        index_html = generate_blog_index()
        if safe_write_file(INDEX_FILE, index_html):
            logger.info(f"✅ Blog index updated: {INDEX_FILE}")
        else:
            logger.error("❌ Failed to update blog index")
            return
        
        logger.info("🎉 Blog generation completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
