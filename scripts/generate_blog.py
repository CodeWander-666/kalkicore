#!/usr/bin/env python3
"""
Enterprise‑grade SEO Blog Generator for SIDDHI AI
Generates one high‑quality blog post per day, targeting the best unused keyword.
"""

import os
import json
import re
import random
import datetime
import requests
from string import punctuation
from pathlib import Path
from collections import defaultdict
import logging

# ---------- CONFIGURATION ----------
SITE_URL = "https://siddhiai.com"          # Change to your actual domain
BLOG_DIR = "blog"
POSTS_DIR = os.path.join(BLOG_DIR, "posts")
INDEX_FILE = os.path.join(BLOG_DIR, "index.html")
KEYWORDS_DB = os.path.join(BLOG_DIR, "keywords_db.json")

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
