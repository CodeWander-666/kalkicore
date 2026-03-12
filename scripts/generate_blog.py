#!/usr/bin/env python3
"""
Enterprise‑grade SEO Blog Generator for SIDDHI AI
Generates one high‑quality blog post per day.
Now with balanced scoring to favor local Indian locations.
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
from typing import List, Dict, Optional, Tuple, Any

import requests

# ---------- CONFIGURATION ----------
SITE_URL = "https://siddhiai.com"          # Change to your actual domain
BLOG_DIR = "blog"
POSTS_DIR = os.path.join(BLOG_DIR, "posts")
INDEX_FILE = os.path.join(BLOG_DIR, "index.html")
KEYWORDS_DB = os.path.join(BLOG_DIR, "keywords_db.json")

# Ensure blog directory exists
os.makedirs(BLOG_DIR, exist_ok=True)

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

# ---------- FALLBACK LSI KEYWORDS (if Datamuse fails) ----------
FALLBACK_LSI = {
    "Web Development": ["frontend", "backend", "full stack", "HTML", "CSS", "JavaScript", "React", "Node.js", "API", "database"],
    "Digital Marketing": ["SEO", "PPC", "social media", "email marketing", "content marketing", "analytics", "conversion", "lead generation"],
    "SEO Services": ["search engine optimization", "keywords", "backlinks", "ranking", "Google", "local SEO", "on-page", "off-page"],
    "Python Training": ["Python basics", "Django", "Flask", "data science", "machine learning", "pandas", "numpy", "automation"],
    "AI Solutions": ["machine learning", "deep learning", "neural networks", "NLP", "computer vision", "chatbots", "predictive analytics"],
    "E-commerce Website": ["online store", "shopping cart", "payment gateway", "product catalog", "inventory", "WooCommerce", "Shopify"],
    "Content Marketing": ["blog posts", "articles", "white papers", "infographics", "video", "storytelling", "brand awareness"],
    "Social Media Marketing": ["Facebook", "Instagram", "Twitter", "LinkedIn", "engagement", "followers", "posts", "ads"],
    "Mobile App Development": ["iOS", "Android", "React Native", "Flutter", "UI/UX", "app store", "mobile design"],
    "Cloud Consulting": ["AWS", "Azure", "Google Cloud", "migration", "serverless", "scalability", "cost optimization"],
    "Data Analytics": ["data visualization", "business intelligence", "Tableau", "Power BI", "SQL", "big data", "insights"],
    "UI/UX Design": ["user interface", "user experience", "wireframes", "prototyping", "usability", "Figma", "Sketch"],
    "Branding": ["logo design", "brand identity", "style guide", "messaging", "positioning", "visual identity"],
    "PPC Advertising": ["Google Ads", "pay per click", "campaign management", "ad copy", "keywords", "ROI", "conversion tracking"],
    "Email Marketing": ["newsletter", "automation", "subscribers", "open rates", "click through", "Mailchimp", "SendGrid"]
}

# ---------- DATA (expand as needed) ----------
TOPICS = list(FALLBACK_LSI.keys())

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

# Opportunity scores (adjusted to favor local)
OPPORTUNITY_POP = {
    "global": 300,    # Reduced to encourage local
    "country": 500,   # India
    "state": 400,
    "city": 300,
    "area": 200
}

# ---------- UTILITY FUNCTIONS ----------
def slugify(text: str) -> str:
    """Convert text to URL‑friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(f"[{re.escape(punctuation)}]", "", text)
    return text

def safe_file_write(filepath: str, content: str) -> bool:
    """Atomically write content to file using a temporary file. Returns True on success."""
    dirname = os.path.dirname(filepath)
    try:
        os.makedirs(dirname, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=dirname, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        shutil.move(tmp_path, filepath)
        logger.debug(f"Successfully written {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to write {filepath}: {e}")
        return False

def fetch_with_retry(url: str, max_retries: int = 3, backoff: float = 1.0) -> Optional[Any]:
    """Fetch URL with exponential backoff retry. Returns parsed JSON or None."""
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
    """Fetch semantically related keywords from Datamuse. Falls back to static list on failure."""
    try:
        url = f"https://api.datamuse.com/words?ml={phrase}&max={max_results}"
        data = fetch_with_retry(url)
        if data:
            return [item['word'] for item in data if 'word' in item]
    except Exception as e:
        logger.exception(f"Unexpected error in fetch_lsi_keywords for '{phrase}': {e}")
    # Fallback to static list
    logger.info(f"Using fallback LSI for '{phrase}'")
    return FALLBACK_LSI.get(phrase, ["guide", "tips", "services", "company", "experts"])[:max_results]

def fetch_related_phrases(phrase: str, max_results: int = 5) -> List[str]:
    """Fetch topic‑related phrases from Datamuse. Falls back to static list."""
    try:
        url = f"https://api.datamuse.com/words?topics={phrase}&max={max_results}"
        data = fetch_with_retry(url)
        if data:
            return [item['word'] for item in data if 'word' in item]
    except Exception as e:
        logger.exception(f"Unexpected error in fetch_related_phrases for '{phrase}': {e}")
    return FALLBACK_LSI.get(phrase, ["resources", "solutions", "providers"])[:max_results]

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
    base = OPPORTUNITY_POP.get(kw["loc_type"], 50)
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
def read_index_template() -> str:
    """Read the existing blog/index.html file. If missing, raise error."""
    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError(f"{INDEX_FILE} not found. Please create it manually using the template.")
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return f.read()

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

    # Read the blog index template (full design)
    template = read_index_template()

    # Replace the main content area with the article.
    main_pattern = r'<main[^>]*>.*?</main>'
    article_main = f"""
    <main class="pt-32 pb-20 interactive-ui max-w-4xl mx-auto px-6">
        <article class="glass-panel p-8 md:p-12 rounded-3xl">
            <h1 class="font-serif text-4xl md:text-5xl text-textmain mb-4">{title}</h1>
            <div class="text-textmuted text-sm mb-8">Published on {date.strftime("%B %d, %Y")}</div>
            {body}
        </article>
    </main>
    """
    post_html = re.sub(main_pattern, article_main, template, flags=re.DOTALL)

    # Replace meta tags
    post_html = re.sub(r'<title>.*?</title>', f'<title>{title} | SIDDHI AI Blog</title>', post_html)
    post_html = re.sub(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{meta_desc}"', post_html)
    post_html = re.sub(r'<meta name="keywords" content="[^"]*"', f'<meta name="keywords" content="{keywords_meta}"', post_html)
    post_html = re.sub(r'<link rel="canonical" href="[^"]*"', f'<link rel="canonical" href="{canonical}"', post_html)

    return post_html

# ---------- BLOG INDEX UPDATE ----------
def update_blog_index() -> None:
    """Scan posts directory and regenerate blog/index.html with all post cards."""
    if not os.path.exists(INDEX_FILE):
        logger.error(f"{INDEX_FILE} not found. Cannot update index. Please create it manually.")
        return

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

    # Generate card HTML safely
    cards_html = ""
    for p in posts:
        # Build tags string without using complex f‑string generators
        tag_spans = []
        for tag in p['tags']:
            tag_spans.append(f'<span class="text-[7px] bg-accent/10 text-accent px-2 py-0.5 rounded-full uppercase tracking-wider">#{tag}</span>')
        tags_html = ''.join(tag_spans)

        # Build the card HTML
        card = f"""
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
        cards_html += card

    # Read existing index
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count how many posts containers exist – should be 1
    container_count = len(re.findall(r'<div id="postsContainer"', content))
    if container_count != 1:
        logger.warning(f"Found {container_count} postsContainer divs. Expected 1. Check your template.")

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
    """Main execution – generates exactly ONE blog post per run."""
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
        if safe_file_write(filepath, html):
            logger.info(f"Article saved to {filepath}")
            # Mark keyword as used
            mark_keyword_used(keywords, kw, os.path.basename(filepath))
            # Update blog index
            update_blog_index()
        else:
            logger.error("Failed to write article. Exiting.")
            return

    except Exception as e:
        logger.exception("Fatal error in main execution")
        raise

if __name__ == "__main__":
    main()
