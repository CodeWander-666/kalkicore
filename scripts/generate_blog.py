#!/usr/bin/env python3
"""
Enterprise‑grade SEO Blog Generator for SIDDHI AI
Generates one high‑quality blog post per day, targeting the best unused keyword.
Includes robust error handling, retries, logging, and fallbacks.
"""

import os
import json
import re
import random
import datetime
import time
import logging
import shutil
import tempfile
from string import punctuation
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

import requests

# ---------- CONFIGURATION ----------
SITE_URL = "https://siddhiai.com"          # Change to your actual domain
BLOG_DIR = "blog"
POSTS_DIR = os.path.join(BLOG_DIR, "posts")
INDEX_FILE = os.path.join(BLOG_DIR, "index.html")
KEYWORDS_DB = os.path.join(BLOG_DIR, "keywords_db.json")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(BLOG_DIR, 'blog_generator.log'), mode='a')
    ]
)
logger = logging.getLogger(__name__)

# ---------- DATA (expand as needed) ----------
TOPICS = [
    "Web Development", "Digital Marketing", "SEO Services",
    "Python Training", "AI Solutions", "E-commerce Website",
    "Content Marketing", "Social Media Marketing",
    "Mobile App Development", "Cloud Consulting", "Data Analytics",
    "UI/UX Design", "Branding", "PPC Advertising", "Email Marketing"
]

GLOBAL = ["United States", "Canada", "United Kingdom", "Australia", "New Zealand"]
COUNTRY = "India"
STATES = {
    "Madhya Pradesh": ["Indore", "Bhopal", "Gwalior", "Jabalpur", "Ujjain"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"]
}
AREAS = {
    "Indore": ["Vijay Nagar", "New Palasia", "Scheme No. 78", "Rajendra Nagar", "Bholaram"],
    "Bangalore": ["Indiranagar", "Whitefield", "Koramangala", "HSR Layout", "Jayanagar"],
    "Mumbai": ["Andheri East", "Bandra West", "Powai", "Goregaon"]
}

MODIFIERS = [
    "", "best", "top", "affordable", "professional", "services",
    "company", "experts", "agency", "cost", "price", "near me", "review",
    "vs", "alternatives", "guide", "tutorial", "how to", "what is"
]

# Scoring weights
LOCATION_WEIGHT = {"area": 3.0, "city": 2.0, "state": 1.0, "country": 0.5, "global": 0.0}
MODIFIER_BONUS = {
    "best": 2.0, "top": 2.0, "affordable": 1.5, "cheap": 1.5,
    "near me": 2.5, "review": 1.8, "vs": 1.8, "how to": 2.0,
    "guide": 1.5, "tutorial": 1.5
}

# ---------- UTILITY FUNCTIONS ----------
def slugify(text: str) -> str:
    """Convert text to URL‑friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(f"[{re.escape(punctuation)}]", "", text)
    return text

def safe_file_write(filepath: str, content: str) -> None:
    """Atomically write content to file using a temporary file."""
    dirname = os.path.dirname(filepath)
    os.makedirs(dirname, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=dirname, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    shutil.move(tmp_path, filepath)
    logger.debug(f"Written {filepath}")

def fetch_with_retry(url: str, max_retries: int = 3, backoff: float = 1.0) -> Optional[Dict]:
    """Fetch URL with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt+1}/{max_retries} failed for {url}: {e}")
            if attempt < max_retries - 1:
                sleep_time = backoff * (2 ** attempt)
                time.sleep(sleep_time)
            else:
                logger.error(f"All retries failed for {url}")
                return None

def fetch_lsi_keywords(phrase: str, max_results: int = 10) -> List[str]:
    """Fetch semantically related keywords from Datamuse."""
    try:
        url = f"https://api.datamuse.com/words?ml={phrase}&max={max_results}"
        data = fetch_with_retry(url)
        if data:
            return [item['word'] for item in data if 'word' in item]
    except Exception as e:
        logger.exception(f"Unexpected error in fetch_lsi_keywords for '{phrase}': {e}")
    return []

def fetch_related_phrases(phrase: str, max_results: int = 5) -> List[str]:
    """Fetch topic‑related phrases from Datamuse."""
    try:
        url = f"https://api.datamuse.com/words?topics={phrase}&max={max_results}"
        data = fetch_with_retry(url)
        if data:
            return [item['word'] for item in data if 'word' in item]
    except Exception as e:
        logger.exception(f"Unexpected error in fetch_related_phrases for '{phrase}': {e}")
    return []

# ---------- KEYWORD GENERATION & SCORING ----------
def generate_keyword_candidates() -> List[Dict]:
    """Generate all possible keyword combinations."""
    candidates = []
    def add(topic: str, location: str, loc_type: str):
        for mod in MODIFIERS:
            if mod:
                kw = f"{mod} {topic} {location}"
            else:
                kw = f"{topic} {location}"
            candidates.append({
                "keyword": re.sub(r'\s+', ' ', kw.strip()),
                "topic": topic,
                "location": location,
                "loc_type": loc_type,
                "modifier": mod if mod else None
            })
    # Global
    for loc in GLOBAL:
        for t in TOPICS:
            add(t, loc, "global")
    # Country
    for t in TOPICS:
        add(t, COUNTRY, "country")
    # States & Cities
    for state, cities in STATES.items():
        for t in TOPICS:
            add(t, state, "state")
            for city in cities:
                add(t, f"{city}, {state}", "city")
                if city in AREAS:
                    for area in AREAS[city]:
                        add(t, f"{area}, {city}", "area")
    # Deduplicate
    seen = set()
    unique = []
    for c in candidates:
        key = c["keyword"]
        if key not in seen:
            seen.add(key)
            unique.append(c)
    logger.info(f"Generated {len(unique)} unique keyword candidates")
    return unique

def score_keyword(kw: Dict) -> float:
    """Calculate difficulty score (lower = easier)."""
    words = kw["keyword"].split()
    score = 1.0
    score += LOCATION_WEIGHT.get(kw["loc_type"], 0.0)
    if kw["modifier"] in MODIFIER_BONUS:
        score += MODIFIER_BONUS[kw["modifier"]]
    # Longer keywords are more specific → lower competition
    if len(words) >= 5:
        score -= 1.0
    elif len(words) >= 4:
        score -= 0.5
    return max(0.1, min(10, score))  # ensure >0

def opportunity_score(kw: Dict) -> float:
    """Estimate traffic potential (higher = better)."""
    pop = {"global": 1000, "country": 500, "state": 200, "city": 100, "area": 30}
    base = pop.get(kw["loc_type"], 50)
    mod_boost = 1.0 if kw["modifier"] else 0.5
    return base * mod_boost

def select_top_keywords(candidates: List[Dict], top_n: int = 200) -> List[Dict]:
    """Score and select top keywords by opportunity/difficulty."""
    for c in candidates:
        c["difficulty"] = score_keyword(c)
        c["opportunity"] = opportunity_score(c)
        c["score"] = c["opportunity"] / (c["difficulty"] + 0.1)
    sorted_cands = sorted(candidates, key=lambda x: x["score"], reverse=True)
    top = sorted_cands[:top_n]
    for t in top:
        t["used"] = False
        t["date_used"] = None
        t["filename"] = None
        t["pillar"] = False
    logger.info(f"Selected top {len(top)} keywords")
    return top

def load_or_generate_keywords() -> List[Dict]:
    """Load existing keyword DB or generate a new one."""
    if os.path.exists(KEYWORDS_DB):
        try:
            with open(KEYWORDS_DB, 'r', encoding='utf-8') as f:
                keywords = json.load(f)
            logger.info(f"Loaded {len(keywords)} keywords from {KEYWORDS_DB}")
            return keywords
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load {KEYWORDS_DB}: {e}. Regenerating.")
    logger.info("Generating new keyword database...")
    candidates = generate_keyword_candidates()
    top = select_top_keywords(candidates, top_n=200)
    safe_file_write(KEYWORDS_DB, json.dumps(top, indent=2))
    return top

def get_next_keyword(keywords: List[Dict]) -> Dict:
    """Return the highest‑scoring unused keyword."""
    unused = [kw for kw in keywords if not kw.get("used", False)]
    if not unused:
        raise RuntimeError("All keywords used. Please refresh the keyword database.")
    unused.sort(key=lambda x: x["score"], reverse=True)
    return unused[0]

def mark_keyword_used(keywords: List[Dict], kw: Dict, filename: str) -> None:
    """Mark a keyword as used and update the JSON file."""
    for item in keywords:
        if item["keyword"] == kw["keyword"] and item["location"] == kw["location"]:
            item["used"] = True
            item["date_used"] = datetime.datetime.now().isoformat()
            item["filename"] = filename
            break
    safe_file_write(KEYWORDS_DB, json.dumps(keywords, indent=2))
    logger.info(f"Marked keyword '{kw['keyword']}' as used.")

def detect_pillars(keywords: List[Dict]) -> None:
    """Mark broad keywords as pillar pages."""
    for kw in keywords:
        if not kw.get("modifier") and kw.get("loc_type") in ("global", "country"):
            kw["pillar"] = True
    safe_file_write(KEYWORDS_DB, json.dumps(keywords, indent=2))
    logger.info("Pillar detection completed.")

# ---------- CONTENT GENERATION ----------
def get_header_footer_templates() -> Tuple[str, str]:
    """
    Return header and footer HTML strings.
    IMPORTANT: Replace the placeholder styles/scripts with your actual site's code.
    """
    # ====== PASTE YOUR EXACT HEADER HTML HERE (from blog/index.html) ======
    header = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
    <meta name="google-site-verification" content="mXzGHeQy9yGNuw8JTuzgXdDUn-gUcj4C65Jt83rcK9A" />
    <meta name="description" content="SEO_DESCRIPTION">
    <meta name="keywords" content="SEO_KEYWORDS">
    <meta name="author" content="SIDDHI AI">
    <link rel="canonical" href="CANONICAL_URL">
    <title>PAGE_TITLE</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cdefs%3E%3Cfilter id='glow' x='-50%25' y='-50%25' width='200%25' height='200%25'%3E%3CfeGaussianBlur stdDeviation='5' result='blur'/%3E%3CfeMerge%3E%3CfeMergeNode in='blur'/%3E%3CfeMergeNode in='blur'/%3E%3CfeMergeNode in='SourceGraphic'/%3E%3C/feMerge%3E%3C/filter%3E%3C/defs%3E%3Crect width='100' height='100' fill='%23020203' rx='15'/%3E%3Ctext x='50' y='75' font-family='sans-serif' font-size='72' font-style='italic' font-weight='normal' fill='%23E5B769' text-anchor='middle' filter='url(%23glow)'%3EAI%3C/text%3E%3Ctext x='50' y='75' font-family='sans-serif' font-size='72' font-style='italic' font-weight='normal' fill='%23FFF8DC' text-anchor='middle'%3EAI%3C/text%3E%3C/svg%3E">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200;300;400;600;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        /* ========== PASTE YOUR EXACT STYLES HERE ========== */
        :root { /* ... */ }
        /* ... */
    </style>
    <script>
        tailwind.config = { /* ... */ };
        function changeTheme(theme) { /* ... */ }
    </script>
    <script id="vertexShader" type="x-shader/x-vertex">/* ... */</script>
    <script id="fragmentShader" type="x-shader/x-fragment">/* ... */</script>
    <script type="importmap">{}</script>
</head>
<body>
    <canvas id="webgl-canvas"></canvas>
    <div class="ambient-overlay"></div>
    <div id="ui-layer" class="relative z-10 w-full">
        <!-- NAVBAR (adjust links to point to ../../index.html) -->
        <nav class="fixed w-full z-50 ...">...</nav>
        <!-- Mobile menu overlay -->
        <div class="mobile-menu-overlay" id="mobileMenuOverlay">...</div>
"""
    # ====== PASTE YOUR EXACT FOOTER HTML HERE ======
    footer = """
        <!-- FOOTER -->
        <footer class="py-12 border-t border-textmain/10 bg-obsidian interactive-ui">...</footer>
    </div>
    <button id="exit-interactive" class="fixed top-8 right-8 ...">...</button>
    <div style="display:none;">python training Bhopal, digital marketing Indore, ...</div>
    <script type="module">
        // ====== PASTE YOUR EXACT JS MODULE HERE (without the hardcoded blogPosts) ======
    </script>
</body>
</html>
"""
    return header, footer

def generate_article_body(keyword: Dict, lsi_terms: List[str], pillar: Optional[Dict] = None) -> str:
    """Generate the main content of the article."""
    topic = keyword["topic"]
    location = keyword["location"]
    modifier = keyword["modifier"] or ""
    keyword_str = keyword["keyword"]

    intro = f"<p>Are you looking for <strong>{keyword_str}</strong>? You've come to the right place. At SIDDHI AI, we specialise in {topic} and have helped numerous clients in {location} achieve outstanding results. In this {'comprehensive guide' if keyword.get('pillar') else 'article'}, we'll cover everything you need to know about {topic} in {location} and why SIDDHI AI is your ideal partner.</p>"

    sections = []

    if keyword.get("pillar"):
        sections.append(f"<h2>Introduction to {topic} in {location}</h2>")
        sections.append(f"<p>{location} has become a thriving hub for {topic}. This guide will walk you through the key aspects, benefits, and strategies for {topic} in {location}.</p>")
        sections.append(f"<h2>Why {location} is Ideal for {topic}</h2>")
        sections.append(f"<p>The business ecosystem in {location} is rapidly evolving, making it a fertile ground for {topic}.</p>")
        sections.append(f"<h2>Key Benefits of {topic}</h2>")
        sections.append("<ul>" + "".join(f"<li>{b}</li>" for b in [
            f"Increased brand visibility in {location}",
            f"Higher conversion rates through targeted strategies",
            f"Cost‑effective solutions tailored to {location}'s market",
            f"Expert support from SIDDHI AI"
        ]) + "</ul>")
        sections.append(f"<h2>Types of {topic} Services We Offer</h2>")
        sections.append("<ul>" + "".join(f"<li>{s}</li>" for s in [
            f"Custom {topic} strategies for {location} businesses",
            f"End‑to‑end implementation and ongoing support",
            f"Affordable packages for startups and SMEs",
            f"Advanced analytics and reporting"
        ]) + "</ul>")
    else:
        if pillar and pillar.get("filename"):
            pillar_url = f"posts/{pillar['filename']}"
            sections.append(f"<p><em>This article is part of our series on <a href='{pillar_url}' class='text-accent underline'>{pillar['keyword']}</a>. For a complete overview, check out our comprehensive guide.</em></p>")
        sections.append(f"<h2>What You Need to Know About {keyword_str}</h2>")
        sections.append(f"<p>{location} businesses are increasingly adopting {topic}. This post focuses specifically on {keyword_str} – a critical aspect of {topic} that can drive significant growth.</p>")
        sections.append(f"<h2>Key Advantages of {keyword_str}</h2>")
        sections.append("<ul>" + "".join(f"<li>{b}</li>" for b in [
            f"Hyper‑targeted approach for {location}",
            f"Maximise ROI with specialised {modifier} strategies",
            f"Quick implementation and measurable results"
        ]) + "</ul>")

    if lsi_terms:
        sections.append(f"<h2>Related Concepts: {', '.join(lsi_terms[:6])}</h2>")
        sections.append(f"<p>When exploring {topic} in {location}, you'll encounter related terms like {', '.join(lsi_terms[:6])}. Understanding these can deepen your knowledge.</p>")

    sections.append(f"<h2>Frequently Asked Questions About {topic} in {location}</h2>")
    faqs = [
        (f"What is the typical cost of {topic} services in {location}?",
         f"Prices vary based on scope. Contact SIDDHI AI for a free quote."),
        (f"How long does it take to see results?",
         f"Most clients see initial improvements within 3‑6 months."),
        (f"Why choose SIDDHI AI?",
         f"SIDDHI AI combines local expertise with global standards, offering tailored strategies and ongoing support.")
    ]
    for q, a in faqs:
        sections.append(f"<h3>{q}</h3><p>{a}</p>")

    cta = f'<p class="mt-8">Ready to leverage <strong>{keyword_str}</strong> for your business? <a href="../../index.html#contact" class="text-accent underline">Contact SIDDHI AI today</a> for a free consultation.</p>'

    return intro + "\n".join(sections) + "\n" + cta

def generate_blog_post(keyword: Dict, all_keywords: List[Dict]) -> str:
    """Generate full HTML for a blog post."""
    # Fetch LSI terms (with fallback)
    lsi = []
    try:
        lsi = fetch_lsi_keywords(keyword["topic"], max_results=10) + fetch_related_phrases(keyword["topic"], max_results=5)
        lsi = list(set(lsi))
        logger.info(f"Fetched {len(lsi)} LSI terms for '{keyword['topic']}'")
    except Exception as e:
        logger.exception(f"LSI fetch failed, continuing without: {e}")

    # Find related pillar
    pillar = next((k for k in all_keywords if k.get("pillar") and k["topic"] == keyword["topic"]), None)

    # Generate body
    body = generate_article_body(keyword, lsi, pillar)

    # Prepare metadata
    title = keyword["keyword"].title()
    meta_desc = f"Looking for {keyword['keyword']}? Our expert guide covers everything about {keyword['topic']} in {keyword['location']}. Trust SIDDHI AI."
    keywords_meta = f"{keyword['topic'].lower()}, {keyword['location'].lower()}, {', '.join(lsi[:8])}"
    canonical = f"{SITE_URL}/blog/posts/{slugify(title)}.html"
    date = datetime.datetime.now()

    # Get templates
    header, footer = get_header_footer_templates()

    # Replace placeholders
    header = (header
        .replace("SEO_DESCRIPTION", meta_desc)
        .replace("SEO_KEYWORDS", keywords_meta)
        .replace("CANONICAL_URL", canonical)
        .replace("PAGE_TITLE", f"{title} | SIDDHI AI Blog")
    )

    main_content = f"""
    <main class="pt-32 pb-20 interactive-ui max-w-4xl mx-auto px-6">
        <article class="glass-panel p-8 md:p-12 rounded-3xl">
            <h1 class="font-serif text-4xl md:text-5xl text-textmain mb-4">{title}</h1>
            <div class="text-textmuted text-sm mb-8">Published on {date.strftime("%B %d, %Y")}</div>
            {body}
        </article>
    </main>
    """

    return header + main_content + footer

# ---------- BLOG INDEX UPDATE ----------
def update_blog_index() -> None:
    """Scan posts directory and regenerate blog/index.html with all post cards."""
    posts = []
    for fname in sorted(os.listdir(POSTS_DIR), reverse=True):
        if not fname.endswith('.html'):
            continue
        filepath = os.path.join(POSTS_DIR, fname)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract title from <h1>
                title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else fname.replace('.html', '').replace('-', ' ').title()
                # Extract excerpt (first 150 chars of body text)
                body_text = re.sub(r'<[^>]+>', '', content)
                excerpt = body_text[:150] + "…" if len(body_text) > 150 else body_text
                # Get tags from meta keywords
                keywords_match = re.search(r'<meta name="keywords" content="([^"]+)"', content, re.IGNORECASE)
                tags = keywords_match.group(1).split(', ')[:3] if keywords_match else []
                date_str = fname[:10]  # YYYY-MM-DD
                posts.append({
                    'filename': fname,
                    'title': title,
                    'excerpt': excerpt,
                    'category': 'Blog',
                    'tags': tags,
                    'date': date_str
                })
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            continue

    # Generate card HTML
    cards_html = ""
    for p in posts:
        tags_html = ''.join(f'<span class="text-[7px] bg-accent/10 text-accent px-2 py-0.5 rounded-full uppercase tracking-wider">#{tag}</span>' for tag in p['tags'])
        cards_html += f"""
        <div class="tilt-wrapper blog-card gsap-reveal">
            <div class="rgb-card">
                <a href="posts/{p['filename']}" class="rgb-content block">
                    <div class="flex justify-between items-start mb-3">
                        <span class="text-[8px] font-bold text-tech uppercase tracking-widest">{p['category']}</span>
                        <span class="text-[8px] text-textmuted">{p['date']}</span>
                    </div>
                    <h3 class="text-lg font-bold text-textmain mb-2 leading-tight">{p['title']}</h3>
                    <p class="text-xs text-textmuted font-light flex-1">{p['excerpt']}</p>
                    <div class="mt-4 flex flex-wrap gap-1">
                        {tags_html}
                    </div>
                    <span class="mt-4 text-[9px] text-tech hover:text-accent transition-colors self-start uppercase tracking-widest font-bold">Read more →</span>
                </a>
            </div>
        </div>
        """

    # Read existing index
    if not os.path.exists(INDEX_FILE):
        logger.error(f"{INDEX_FILE} not found. Cannot update.")
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace posts container
    pattern = r'(<div id="postsContainer"[^>]*>).*?(</div>)'
    replacement = r'\1' + cards_html + r'\2'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Update JSON‑LD
    schema = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "SIDDHI AI Blog",
        "description": "Expert articles on Python, digital marketing, web development, and AI solutions.",
        "url": f"{SITE_URL}/blog/",
        "blogPost": [
            {"@type": "BlogPosting", "headline": p['title'], "datePublished": p['date'], "url": f"{SITE_URL}/blog/posts/{p['filename']}"}
            for p in posts[:10]
        ]
    }
    schema_str = json.dumps(schema, indent=2, ensure_ascii=False)
    new_content = re.sub(r'<script type="application/ld\+json" id="blogSchema">.*?</script>',
                         f'<script type="application/ld+json" id="blogSchema">{schema_str}</script>',
                         new_content, flags=re.DOTALL)

    # Write back atomically
    safe_file_write(INDEX_FILE, new_content)
    logger.info(f"Blog index updated with {len(posts)} posts.")

# ---------- MAIN ----------
def main() -> None:
    """Main execution."""
    try:
        os.makedirs(POSTS_DIR, exist_ok=True)

        # Load or generate keyword database
        keywords = load_or_generate_keywords()

        # Run pillar detection (only once in a while; here we run it always for simplicity)
        detect_pillars(keywords)

        # Get next keyword
        kw = get_next_keyword(keywords)
        logger.info(f"Selected keyword: {kw['keyword']} (difficulty={kw['difficulty']:.2f}, opportunity={kw['opportunity']:.2f})")

        # Generate post HTML
        html = generate_blog_post(kw, keywords)

        # Create filename
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        base_filename = f"{date_str}-{slugify(kw['keyword'])}.html"
        filepath = os.path.join(POSTS_DIR, base_filename)

        # Avoid overwriting
        counter = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(base_filename)
            filepath = os.path.join(POSTS_DIR, f"{name}-{counter}{ext}")
            counter += 1

        # Write post
        safe_file_write(filepath, html)
        logger.info(f"Article saved to {filepath}")

        # Mark keyword as used
        mark_keyword_used(keywords, kw, os.path.basename(filepath))

        # Update blog index
        update_blog_index()

    except Exception as e:
        logger.exception("Fatal error in main execution")
        raise

if __name__ == "__main__":
    main()
GLOBAL = ["United States", "Canada", "United Kingdom", "Australia", "New Zealand"]
COUNTRY = "India"
STATES = {
    "Madhya Pradesh": ["Indore", "Bhopal", "Gwalior", "Jabalpur", "Ujjain"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"]
}
AREAS = {
    "Indore": ["Vijay Nagar", "New Palasia", "Scheme No. 78", "Rajendra Nagar", "Bholaram"],
    "Bangalore": ["Indiranagar", "Whitefield", "Koramangala", "HSR Layout", "Jayanagar"],
    "Mumbai": ["Andheri East", "Bandra West", "Powai", "Goregaon"]
}

MODIFIERS = [
    "", "best", "top", "affordable", "professional", "services",
    "company", "experts", "agency", "cost", "price", "near me", "review",
    "vs", "alternatives", "guide", "tutorial", "how to", "what is"
]

# Scoring weights
LOCATION_WEIGHT = {"area": 3.0, "city": 2.0, "state": 1.0, "country": 0.5, "global": 0.0}
MODIFIER_BONUS = {
    "best": 2.0, "top": 2.0, "affordable": 1.5, "cheap": 1.5,
    "near me": 2.5, "review": 1.8, "vs": 1.8, "how to": 2.0,
    "guide": 1.5, "tutorial": 1.5
}

# ---------- UTILITY FUNCTIONS ----------
def slugify(text):
    text = text.lower().replace(" ", "-")
    text = re.sub(f"[{re.escape(punctuation)}]", "", text)
    return text

def fetch_lsi_keywords(phrase, max_results=10):
    try:
        url = f"https://api.datamuse.com/words?ml={phrase}&max={max_results}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return [item['word'] for item in resp.json()]
    except Exception as e:
        logger.warning(f"Datamuse error for '{phrase}': {e}")
    return []

def fetch_related_phrases(phrase, max_results=5):
    try:
        url = f"https://api.datamuse.com/words?topics={phrase}&max={max_results}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return [item['word'] for item in resp.json()]
    except Exception as e:
        logger.warning(f"Datamuse topics error for '{phrase}': {e}")
    return []

# ---------- KEYWORD GENERATION & SCORING ----------
def generate_keyword_candidates():
    candidates = []
    def add(topic, location, loc_type):
        for mod in MODIFIERS:
            if mod:
                kw = f"{mod} {topic} {location}"
            else:
                kw = f"{topic} {location}"
            candidates.append({
                "keyword": re.sub(r'\s+', ' ', kw.strip()),
                "topic": topic,
                "location": location,
                "loc_type": loc_type,
                "modifier": mod if mod else None
            })
    # Global
    for loc in GLOBAL:
        for t in TOPICS:
            add(t, loc, "global")
    # Country
    for t in TOPICS:
        add(t, COUNTRY, "country")
    # States & Cities
    for state, cities in STATES.items():
        for t in TOPICS:
            add(t, state, "state")
            for city in cities:
                add(t, f"{city}, {state}", "city")
                if city in AREAS:
                    for area in AREAS[city]:
                        add(t, f"{area}, {city}", "area")
    # Deduplicate
    unique = {}
    for c in candidates:
        key = c["keyword"]
        if key not in unique:
            unique[key] = c
    return list(unique.values())

def score_keyword(kw):
    words = kw["keyword"].split()
    score = 1.0
    score += LOCATION_WEIGHT.get(kw["loc_type"], 0.0)
    if kw["modifier"] in MODIFIER_BONUS:
        score += MODIFIER_BONUS[kw["modifier"]]
    # Longer keywords are more specific → lower competition
    if len(words) >= 5:
        score -= 1.0
    elif len(words) >= 4:
        score -= 0.5
    return max(0, min(10, score))

def opportunity_score(kw):
    # Higher for more populous locations
    pop = {"global": 1000, "country": 500, "state": 200, "city": 100, "area": 30}
    base = pop.get(kw["loc_type"], 50)
    mod_boost = 1.0 if kw["modifier"] else 0.5
    return base * mod_boost

def select_top_keywords(candidates, top_n=200):
    for c in candidates:
        c["difficulty"] = score_keyword(c)
        c["opportunity"] = opportunity_score(c)
        c["score"] = c["opportunity"] / (c["difficulty"] + 0.1)
    sorted_cands = sorted(candidates, key=lambda x: x["score"], reverse=True)
    top = sorted_cands[:top_n]
    for t in top:
        t["used"] = False
        t["date_used"] = None
        t["filename"] = None
        t["pillar"] = False
    return top

def load_or_generate_keywords():
    if os.path.exists(KEYWORDS_DB):
        with open(KEYWORDS_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    logger.info("Generating keyword candidates...")
    candidates = generate_keyword_candidates()
    logger.info(f"→ {len(candidates)} unique candidates.")
    top = select_top_keywords(candidates, top_n=200)
    logger.info(f"→ Top 200 selected.")
    with open(KEYWORDS_DB, 'w', encoding='utf-8') as f:
        json.dump(top, f, indent=2)
    return top

def get_next_keyword(keywords):
    unused = [kw for kw in keywords if not kw["used"]]
    if not unused:
        raise Exception("All keywords used. Refresh the database.")
    unused.sort(key=lambda x: x["score"], reverse=True)
    return unused[0]

def mark_keyword_used(keywords, kw, filename):
    for item in keywords:
        if item["keyword"] == kw["keyword"] and item["location"] == kw["location"]:
            item["used"] = True
            item["date_used"] = datetime.datetime.now().isoformat()
            item["filename"] = filename
            break
    with open(KEYWORDS_DB, 'w', encoding='utf-8') as f:
        json.dump(keywords, f, indent=2)

def detect_pillars(keywords):
    # Mark broad keywords as pillars (e.g., no modifier, location type global/country)
    for kw in keywords:
        if not kw["modifier"] and kw["loc_type"] in ("global", "country"):
            kw["pillar"] = True
    with open(KEYWORDS_DB, 'w', encoding='utf-8') as f:
        json.dump(keywords, f, indent=2)

# ---------- CONTENT GENERATION ----------
def get_header_footer_templates():
    """
    Return header and footer HTML strings.
    These should be copied exactly from your main index.html,
    with relative links adjusted.
    """
    header = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
    <meta name="google-site-verification" content="mXzGHeQy9yGNuw8JTuzgXdDUn-gUcj4C65Jt83rcK9A" />
    <meta name="description" content="SEO_DESCRIPTION">
    <meta name="keywords" content="SEO_KEYWORDS">
    <meta name="author" content="SIDDHI AI">
    <link rel="canonical" href="CANONICAL_URL">
    <title>PAGE_TITLE</title>
    <!-- Favicon, Tailwind, Icons, Fonts, Styles (copy from blog/index.html) -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,..." />
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@200;300;400;600;800&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        /* Paste the entire <style> block from blog/index.html here */
    </style>
    <script>
        tailwind.config = { /* ... */ };
        function changeTheme(theme) { /* ... */ }
    </script>
    <!-- Shaders and import map (same) -->
    <script id="vertexShader" type="x-shader/x-vertex">...</script>
    <script id="fragmentShader" type="x-shader/x-fragment">...</script>
    <script type="importmap">...</script>
</head>
<body>
    <canvas id="webgl-canvas"></canvas>
    <div class="ambient-overlay"></div>
    <div id="ui-layer" class="relative z-10 w-full">
        <!-- NAVBAR (copy from blog/index.html, adjust links to point to ../../index.html) -->
        <nav class="fixed w-full z-50 ...">...</nav>
        <!-- Mobile menu overlay -->
        <div class="mobile-menu-overlay" id="mobileMenuOverlay">...</div>
"""
    footer = """
        <!-- FOOTER (copy from blog/index.html) -->
        <footer class="py-12 border-t border-textmain/10 bg-obsidian interactive-ui">...</footer>
    </div>
    <button id="exit-interactive" class="fixed top-8 right-8 ...">...</button>
    <div style="display:none;">python training Bhopal, digital marketing Indore, ...</div>
    <script type="module">
        // Paste the full JS module from blog/index.html (without the hardcoded blogPosts)
    </script>
</body>
</html>
"""
    return header, footer

def generate_article_body(keyword, lsi_terms, pillar=None):
    topic = keyword["topic"]
    location = keyword["location"]
    modifier = keyword["modifier"] or ""
    keyword_str = keyword["keyword"]

    intro = f"<p>Are you looking for <strong>{keyword_str}</strong>? You've come to the right place. At SIDDHI AI, we specialise in {topic} and have helped numerous clients in {location} achieve outstanding results. In this {'comprehensive guide' if keyword.get('pillar') else 'article'}, we'll cover everything you need to know about {topic} in {location} and why SIDDHI AI is your ideal partner.</p>"

    sections = []

    if keyword.get("pillar"):
        sections.append(f"<h2>Introduction to {topic} in {location}</h2>")
        sections.append(f"<p>{location} has become a thriving hub for {topic}. This guide will walk you through the key aspects, benefits, and strategies for {topic} in {location}.</p>")
        sections.append(f"<h2>Why {location} is Ideal for {topic}</h2>")
        sections.append(f"<p>The business ecosystem in {location} is rapidly evolving, making it a fertile ground for {topic}.</p>")
        sections.append(f"<h2>Key Benefits of {topic}</h2>")
        sections.append("<ul>" + "".join(f"<li>{b}</li>" for b in [
            f"Increased brand visibility in {location}",
            f"Higher conversion rates through targeted strategies",
            f"Cost‑effective solutions tailored to {location}'s market",
            f"Expert support from SIDDHI AI"
        ]) + "</ul>")
        sections.append(f"<h2>Types of {topic} Services We Offer</h2>")
        sections.append("<ul>" + "".join(f"<li>{s}</li>" for s in [
            f"Custom {topic} strategies for {location} businesses",
            f"End‑to‑end implementation and ongoing support",
            f"Affordable packages for startups and SMEs",
            f"Advanced analytics and reporting"
        ]) + "</ul>")
    else:
        if pillar:
            pillar_url = f"posts/{pillar['filename']}"
            sections.append(f"<p><em>This article is part of our series on <a href='{pillar_url}' class='text-accent underline'>{pillar['keyword']}</a>. For a complete overview, check out our comprehensive guide.</em></p>")
        sections.append(f"<h2>What You Need to Know About {keyword_str}</h2>")
        sections.append(f"<p>{location} businesses are increasingly adopting {topic}. This post focuses specifically on {keyword_str} – a critical aspect of {topic} that can drive significant growth.</p>")
        sections.append(f"<h2>Key Advantages of {keyword_str}</h2>")
        sections.append("<ul>" + "".join(f"<li>{b}</li>" for b in [
            f"Hyper‑targeted approach for {location}",
            f"Maximise ROI with specialised {modifier} strategies",
            f"Quick implementation and measurable results"
        ]) + "</ul>")

    if lsi_terms:
        sections.append(f"<h2>Related Concepts: {', '.join(lsi_terms[:6])}</h2>")
        sections.append(f"<p>When exploring {topic} in {location}, you'll encounter related terms like {', '.join(lsi_terms[:6])}. Understanding these can deepen your knowledge.</p>")

    sections.append(f"<h2>Frequently Asked Questions About {topic} in {location}</h2>")
    faqs = [
        (f"What is the typical cost of {topic} services in {location}?",
         f"Prices vary based on scope. Contact SIDDHI AI for a free quote."),
        (f"How long does it take to see results?",
         f"Most clients see initial improvements within 3‑6 months."),
        (f"Why choose SIDDHI AI?",
         f"SIDDHI AI combines local expertise with global standards, offering tailored strategies and ongoing support.")
    ]
    for q, a in faqs:
        sections.append(f"<h3>{q}</h3><p>{a}</p>")

    cta = f'<p class="mt-8">Ready to leverage <strong>{keyword_str}</strong> for your business? <a href="../../index.html#contact" class="text-accent underline">Contact SIDDHI AI today</a> for a free consultation.</p>'

    return intro + "\n".join(sections) + "\n" + cta

def generate_blog_post(keyword, all_keywords):
    lsi = fetch_lsi_keywords(keyword["topic"], max=10) + fetch_related_phrases(keyword["topic"], max=5)
    lsi = list(set(lsi))
    pillar = next((k for k in all_keywords if k.get("pillar") and k["topic"] == keyword["topic"]), None)
    body = generate_article_body(keyword, lsi, pillar)

    title = keyword["keyword"].title()
    meta_desc = f"Looking for {keyword['keyword']}? Our expert guide covers everything about {keyword['topic']} in {keyword['location']}. Trust SIDDHI AI."
    keywords_meta = f"{keyword['topic'].lower()}, {keyword['location'].lower()}, {', '.join(lsi[:8])}"
    canonical = f"{SITE_URL}/blog/posts/{slugify(title)}.html"
    date = datetime.datetime.now()

    header, footer = get_header_footer_templates()
    # Replace placeholders
    header = (header
        .replace("SEO_DESCRIPTION", meta_desc)
        .replace("SEO_KEYWORDS", keywords_meta)
        .replace("CANONICAL_URL", canonical)
        .replace("PAGE_TITLE", f"{title} | SIDDHI AI Blog")
    )
    main_content = f"""
    <main class="pt-32 pb-20 interactive-ui max-w-4xl mx-auto px-6">
        <article class="glass-panel p-8 md:p-12 rounded-3xl">
            <h1 class="font-serif text-4xl md:text-5xl text-textmain mb-4">{title}</h1>
            <div class="text-textmuted text-sm mb-8">Published on {date.strftime("%B %d, %Y")}</div>
            {body}
        </article>
    </main>
    """
    return header + main_content + footer

def update_blog_index():
    posts = []
    for fname in sorted(os.listdir(POSTS_DIR), reverse=True):
        if not fname.endswith('.html'):
            continue
        filepath = os.path.join(POSTS_DIR, fname)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', content)
            title = title_match.group(1) if title_match else fname.replace('.html', '').replace('-', ' ').title()
            body_text = re.sub(r'<[^>]+>', '', content)
            excerpt = body_text[:150] + "…" if len(body_text) > 150 else body_text
            keywords_match = re.search(r'<meta name="keywords" content="([^"]+)"', content)
            tags = keywords_match.group(1).split(', ')[:3] if keywords_match else []
            date_str = fname[:10]
            posts.append({
                'filename': fname,
                'title': title,
                'excerpt': excerpt,
                'category': 'Blog',
                'tags': tags,
                'date': date_str
            })

    cards_html = ""
    for p in posts:
        tags_html = ''.join(f'<span class="text-[7px] bg-accent/10 text-accent px-2 py-0.5 rounded-full uppercase tracking-wider">#{tag}</span>' for tag in p['tags'])
        cards_html += f"""
        <div class="tilt-wrapper blog-card gsap-reveal">
            <div class="rgb-card">
                <a href="posts/{p['filename']}" class="rgb-content block">
                    <div class="flex justify-between items-start mb-3">
                        <span class="text-[8px] font-bold text-tech uppercase tracking-widest">{p['category']}</span>
                        <span class="text-[8px] text-textmuted">{p['date']}</span>
                    </div>
                    <h3 class="text-lg font-bold text-textmain mb-2 leading-tight">{p['title']}</h3>
                    <p class="text-xs text-textmuted font-light flex-1">{p['excerpt']}</p>
                    <div class="mt-4 flex flex-wrap gap-1">
                        {tags_html}
                    </div>
                    <span class="mt-4 text-[9px] text-tech hover:text-accent transition-colors self-start uppercase tracking-widest font-bold">Read more →</span>
                </a>
            </div>
        </div>
        """

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    pattern = r'(<div id="postsContainer"[^>]*>).*?(</div>)'
    replacement = r'\1' + cards_html + r'\2'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Update JSON‑LD
    schema = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "SIDDHI AI Blog",
        "description": "Expert articles on Python, digital marketing, web development, and AI solutions.",
        "url": f"{SITE_URL}/blog/",
        "blogPost": [
            {"@type": "BlogPosting", "headline": p['title'], "datePublished": p['date'], "url": f"{SITE_URL}/blog/posts/{p['filename']}"}
            for p in posts[:10]
        ]
    }
    schema_str = json.dumps(schema, indent=2)
    new_content = re.sub(r'<script type="application/ld\+json" id="blogSchema">.*?</script>',
                         f'<script type="application/ld+json" id="blogSchema">{schema_str}</script>',
                         new_content, flags=re.DOTALL)

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    logger.info(f"Blog index updated with {len(posts)} posts.")

def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    keywords = load_or_generate_keywords()
    detect_pillars(keywords)  # run once; in production you might do this monthly

    try:
        kw = get_next_keyword(keywords)
    except Exception as e:
        logger.error(e)
        return

    logger.info(f"Generating article for: {kw['keyword']} (difficulty {kw['difficulty']:.2f}, opportunity {kw['opportunity']:.2f})")

    html = generate_blog_post(kw, keywords)

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    base_filename = f"{date_str}-{slugify(kw['keyword'])}.html"
    filepath = os.path.join(POSTS_DIR, base_filename)

    counter = 1
    while os.path.exists(filepath):
        name, ext = os.path.splitext(base_filename)
        filepath = os.path.join(POSTS_DIR, f"{name}-{counter}{ext}")
        counter += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    logger.info(f"Article saved to {filepath}")
    mark_keyword_used(keywords, kw, os.path.basename(filepath))
    update_blog_index()

if __name__ == "__main__":
    main()
