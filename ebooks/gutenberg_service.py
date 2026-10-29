"""
LibrarySphere Project Gutenberg Integration Service.
Fetches, cleans, and formats authentic, complete, illustrated Project Gutenberg
editions for world literature classics. Rewrites image URLs to high-resolution
Gutenberg mirrors and slices content into publisher-grade reader pages.
"""

import os
import re
import ssl
import urllib.request
from pathlib import Path
from typing import Optional, Tuple, List
from django.conf import settings


class GutenbergService:
    """Manages authentic Project Gutenberg illustrated editions."""

    GUTENBERG_MAPPING = {
        'pride and prejudice': 1342,
        'frankenstein': 84,
        'the adventures of sherlock holmes': 1661,
        'adventures of sherlock holmes': 1661,
        'sherlock holmes': 1661,
        'dracula': 345,
        'alice in wonderland': 11,
        'alices adventures in wonderland': 11,
        "alice's adventures in wonderland": 11,
        'the great gatsby': 64317,
        'great gatsby': 64317,
        'the time machine': 35,
        'time machine': 35,
        'the metamorphosis': 5200,
        'metamorphosis': 5200,
        'a tale of two cities': 98,
        'tale of two cities': 98,
        'moby-dick': 2701,
        'moby-dick; or, the whale': 2701,
        'moby dick': 2701,
        'the picture of dorian gray': 174,
        'picture of dorian gray': 174,
        'jane eyre': 1260,
        'wuthering heights': 768,
        'crime and punishment': 2554,
        'the brothers karamazov': 28054,
        'brothers karamazov': 28054,
        'war and peace': 2600,
        'anna karenina': 1399,
        'don quixote': 996,
        'the count of monte cristo': 1184,
        'count of monte cristo': 1184,
        'the republic': 1497,
        'the prince': 1232,
        'meditations': 2680,
        'discourse on method': 59,
        'yellow wallpaper': 1952,
        'heart of darkness': 219,
        'the scarlet letter': 33,
        'leaves of grass': 1322,
        'dubliners': 2814,
        'strange case of dr jekyll': 43,
        'dr jekyll and mr hyde': 43,
        'treasure island': 120,
        'robinson crusoe': 524,
        'gullivers travels': 829,
        "gulliver's travels": 829,
        'sense and sensibility': 161,
        'emma': 158,
        'persuasion': 105,
        'northanger abbey': 121,
        'the call of the wild': 215,
        'call of the wild': 215,
        'the war of the worlds': 36,
        'war of the worlds': 36,
        'the invisible man': 5230,
        'invisible man': 5230,
    }

    @classmethod
    def get_gutenberg_id_for_title(cls, title: str) -> Optional[int]:
        """Resolves a book title to a Project Gutenberg ID with strict boundary matching to avoid false positives."""
        clean = re.sub(r'[^a-z0-9\s]', '', title.lower()).strip()
        words = clean.split()

        # Guard against modern works containing substring words
        if 'space' in words and 'odyssey' in words:
            return None
        if 'psychology' in words and 'persuasion' in words:
            return None
        if 'dilemma' in words:
            return None

        for k, gid in cls.GUTENBERG_MAPPING.items():
            k_clean = re.sub(r'[^a-z0-9\s]', '', k.lower()).strip()
            pattern = r'\b' + re.escape(k_clean) + r'\b'
            if re.search(pattern, clean):
                return gid
        return None

    @classmethod
    def fetch_raw_gutenberg_html(cls, gid: int) -> Optional[str]:
        """Fetches the raw illustrated HTML document for a Gutenberg ID, using local cache when available."""
        cache_dir = Path(settings.BASE_DIR) / 'data' / 'gutenberg_cache'
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = cache_dir / f"pg{gid}.html"

        if cache_file.exists() and cache_file.stat().st_size > 50000:
            try:
                return cache_file.read_text(encoding='utf-8', errors='replace')
            except Exception:
                pass

        urls = [
            f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}-images.html",
            f"https://www.gutenberg.org/files/{gid}/{gid}-h/{gid}-h.htm"
        ]

        ctx = ssl._create_unverified_context()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        for url in urls:
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                    if resp.status == 200:
                        content = resp.read().decode('utf-8', errors='replace')
                        if len(content) > 20000:
                            try:
                                cache_file.write_text(content, encoding='utf-8')
                            except Exception:
                                pass
                            return content
            except Exception:
                continue

        return None

    @classmethod
    def balance_html(cls, fragment: str) -> str:
        """Closes any unclosed HTML tags at the end of a page slice."""
        open_tags = []
        for tag_match in re.finditer(r'<(/)?([a-zA-Z0-9]+)(?:\s+[^>]*)?>', fragment):
            is_closing = bool(tag_match.group(1))
            tag_name = tag_match.group(2).lower()
            if tag_name in ['img', 'br', 'hr', 'meta', 'link', 'input', 'source']:
                continue
            if is_closing:
                if tag_name in open_tags:
                    while open_tags and open_tags[-1] != tag_name:
                        open_tags.pop()
                    if open_tags:
                        open_tags.pop()
            else:
                open_tags.append(tag_name)
        for tag in reversed(open_tags):
            fragment += f"</{tag}>"
        return fragment

    @classmethod
    def format_gutenberg_reader_document(cls, title: str, author: str, gid: int) -> Optional[Tuple[str, int]]:
        """
        Transforms raw Gutenberg HTML into a publisher-grade, paginated digital reader edition.
        Returns (full_html, total_pages).
        """
        raw_html = cls.fetch_raw_gutenberg_html(gid)
        if not raw_html:
            return None

        # 1. Clean boilerplate headers & footers
        start_match = re.search(r'start of (?:the )?project gutenberg', raw_html, re.I)
        start_pos = start_match.end() if start_match else 0
        end_match = re.search(r'end of (?:the )?project gutenberg', raw_html, re.I)
        end_pos = end_match.start() if end_match else len(raw_html)

        body = raw_html[start_pos:end_pos]
        body = re.sub(r'^.*?<div class=[\"\']blk[\"\']', '<div class=\"blk\"', body, flags=re.DOTALL)
        body = re.sub(r'^.*?<h1', '<h1', body, flags=re.DOTALL)

        # 2. Rewrite image sources to absolute Gutenberg mirror
        body = re.sub(r'src=[\"\']images/([^\"\']+)[\"\']', f'src=\"https://www.gutenberg.org/cache/epub/{gid}/images/\\1\"', body)
        body = re.sub(r'href=[\"\']images/([^\"\']+)[\"\']', f'href=\"https://www.gutenberg.org/cache/epub/{gid}/images/\\1\"', body)

        # 3. Detect and slice pages
        markers = list(re.finditer(r'<span class=[\"\']pagenum[\"\']><a id=[\"\']page_([^\"\']+)[\"\']>\{([^}]+)\}</a></span>', body))

        pages_data = []
        if len(markers) >= 30:
            clean_starts = []
            for m in markers:
                s = m.start()
                # If a heading opened just before s, include it in this page slice
                prefix = body[max(0, s - 120):s]
                h_match = re.search(r'(<h[1-6][^>]*>(?:<a[^>]*></a>)?)\s*$', prefix, re.IGNORECASE)
                if h_match:
                    s = s - len(h_match.group(0))
                clean_starts.append(s)

            for i in range(len(markers)):
                s = clean_starts[i]
                e = clean_starts[i + 1] if i + 1 < len(clean_starts) else len(body)
                label = markers[i].group(2)
                chunk = cls.balance_html(body[s:e])
                pages_data.append((label, chunk))
        else:
            # Paragraph-level book pagination (~280 words per page)
            body_unwrapped = re.sub(r'</?div[^>]*>', '', body)
            elements = re.split(r'(?=<p[^>]*>|<h[1-6][^>]*>)', body_unwrapped)
            cur_chunk = []
            cur_words = 0
            page_idx = 1
            for el in elements:
                w = len(re.sub(r'<[^>]+>', ' ', el).split())
                is_heading = bool(re.match(r'^\s*<h[1-2][^>]*>', el, re.IGNORECASE))
                if is_heading and cur_words >= 100:
                    pages_data.append((str(page_idx), cls.balance_html("".join(cur_chunk))))
                    cur_chunk = [el]
                    cur_words = w
                    page_idx += 1
                    continue
                cur_chunk.append(el)
                cur_words += w
                if cur_words >= 280:
                    pages_data.append((str(page_idx), cls.balance_html("".join(cur_chunk))))
                    cur_chunk = []
                    cur_words = 0
                    page_idx += 1
            if cur_chunk:
                pages_data.append((str(page_idx), cls.balance_html("".join(cur_chunk))))

        if not pages_data:
            return None

        total_pages = len(pages_data)

        # 4. Wrap each page into .book-page with running header and footer
        pages_html = []
        for i, (label, chunk) in enumerate(pages_data):
            actual_p = i + 1
            pages_html.append(f"""
            <section class="book-page" id="page-{actual_p}" data-page="{actual_p}">
                <div class="page-header">
                    <span class="header-title">{title}</span>
                    <span class="header-chapter">{author} &bull; Illustrated Edition</span>
                </div>
                <div class="page-content">
                    {chunk}
                </div>
                <div class="page-footer">
                    <span class="footer-license">Project Gutenberg Illustrated Edition</span>
                    <span class="page-number">— {label} ({actual_p} of {total_pages}) —</span>
                </div>
            </section>
            """)

        # 5. Assemble complete document with authentic classical book styling
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Complete {total_pages}-Page Illustrated Edition</title>
    <style>
        :root {{
            --primary: #1e1b4b;
            --accent: #b45309;
            --border: #e2e8f0;
            --bg-page: #ffffff;
            --text-main: #1c1917;
            --text-muted: #78716c;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: Georgia, "Palatino Linotype", "Book Antiqua", Palatino, serif;
            line-height: 1.75;
            color: var(--text-main);
            background-color: #f1f5f9;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }}
        .book-container {{
            max-width: 860px;
            margin: 0 auto;
            padding: 1.5rem 1rem 5rem 1rem;
        }}
        .book-page {{
            background: var(--bg-page);
            width: 100%;
            max-width: 800px;
            min-height: 1050px;
            margin: 2rem auto;
            padding: 3.5rem 4rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.04);
            border-radius: 4px;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            page-break-after: always;
            transition: all 0.2s ease-in-out;
        }}
        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 0.75rem;
            margin-bottom: 2rem;
        }}
        .page-content {{
            flex-grow: 1;
            font-size: 1.05rem;
            color: #1c1917;
            text-align: justify;
            text-justify: inter-word;
        }}
        .page-content p {{
            text-indent: 1.5em;
            margin-top: 0;
            margin-bottom: 0.65em;
            line-height: 1.75;
        }}
        .page-content p.nind, .page-content p.c, .page-content .center {{
            text-indent: 0 !important;
            text-align: center;
        }}
        .page-content img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5rem auto;
            border-radius: 2px;
        }}
        .page-content h1, .page-content h2, .page-content h3 {{
            text-align: center;
            font-family: Georgia, serif;
            font-weight: normal;
            margin: 1.5rem 0 1rem 0;
            letter-spacing: 0.8px;
            color: #0f172a;
        }}
        .page-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 0.78rem;
            color: var(--text-muted);
            border-top: 1px solid #e2e8f0;
            padding-top: 0.75rem;
            margin-top: 2rem;
        }}
        .page-number {{
            font-weight: 700;
            color: #334155;
            font-family: monospace;
            font-size: 0.85rem;
        }}
        .pagenum {{
            float: right;
            font-size: 0.78rem;
            color: #a8a29e;
            font-family: monospace;
            margin-left: 0.5rem;
        }}
        span.letra {{
            font-size: 320%;
            float: left;
            line-height: 80%;
            padding-right: 0.15em;
            font-family: Georgia, serif;
        }}
        span.smcap {{
            font-variant: small-caps;
            letter-spacing: 0.6px;
        }}
        table {{
            margin: 1.5rem auto;
            border-collapse: collapse;
        }}
        td, th {{
            padding: 0.35rem 0.75rem;
        }}

        body.mode-single .book-page {{
            display: none;
            margin: 0 auto;
            min-height: 92vh;
        }}
        body.mode-single .book-page.active-page {{
            display: flex;
        }}

        body.mode-continuous .book-page {{
            display: flex;
            margin-bottom: 2.5rem;
        }}

        .embedded-nav {{
            position: fixed;
            bottom: 1.25rem;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(8px);
            color: #ffffff;
            padding: 0.5rem 1.25rem;
            border-radius: 9999px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
            display: flex;
            align-items: center;
            gap: 1rem;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 0.85rem;
            z-index: 9999;
        }}
        .embedded-nav button {{
            background: rgba(255, 255, 255, 0.15);
            color: #ffffff;
            border: none;
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        }}
        .embedded-nav input {{
            width: 55px;
            text-align: center;
            background: #ffffff;
            color: #0f172a;
            border: none;
            border-radius: 4px;
            font-weight: 700;
            padding: 0.25rem;
        }}

        @media print {{
            body {{ background: #ffffff !important; }}
            .embedded-nav {{ display: none !important; }}
            .book-page {{ box-shadow: none !important; margin: 0 !important; padding: 2cm !important; }}
        }}
    </style>
</head>
<body class="mode-single" id="readerBody">

<div class="book-container">
    {''.join(pages_html)}
</div>

<div class="embedded-nav" id="embeddedNav">
    <button onclick="gotoPrevPage()" title="Previous Page">&larr; Prev</button>
    <span>Page <input type="number" id="navPageInput" min="1" max="{total_pages}" value="1" onchange="onPageInputChange(this.value)"> of <strong>{total_pages}</strong></span>
    <button onclick="gotoNextPage()" title="Next Page">Next &rarr;</button>
    <button onclick="toggleViewMode()" id="viewModeBtn" style="font-size: 0.75rem; background: rgba(255,255,255,0.1);">Mode: Single</button>
</div>

<script>
const TOTAL_PAGES = {total_pages};
let currentPage = 1;
let currentMode = 'single';

function initReader() {{
    const hash = window.location.hash;
    if (hash && hash.startsWith('#page-')) {{
        const p = parseInt(hash.replace('#page-', ''));
        if (!isNaN(p) && p >= 1 && p <= TOTAL_PAGES) {{
            currentPage = p;
        }}
    }}
    applyPage(currentPage);
    notifyParent();
}}

function applyPage(pageNum) {{
    if (pageNum < 1) pageNum = 1;
    if (pageNum > TOTAL_PAGES) pageNum = TOTAL_PAGES;
    currentPage = pageNum;

    const inputEl = document.getElementById('navPageInput');
    if (inputEl) inputEl.value = currentPage;

    if (currentMode === 'single') {{
        const allPages = document.querySelectorAll('.book-page');
        allPages.forEach(el => el.classList.remove('active-page'));
        const targetEl = document.getElementById('page-' + currentPage);
        if (targetEl) {{
            targetEl.classList.add('active-page');
            window.scrollTo({{ top: 0, behavior: 'instant' }});
        }}
    }} else {{
        const targetEl = document.getElementById('page-' + currentPage);
        if (targetEl) {{
            targetEl.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
    }}

    notifyParent();
}}

function gotoPrevPage() {{
    if (currentPage > 1) applyPage(currentPage - 1);
}}

function gotoNextPage() {{
    if (currentPage < TOTAL_PAGES) applyPage(currentPage + 1);
}}

function onPageInputChange(val) {{
    const p = parseInt(val);
    if (!isNaN(p)) applyPage(p);
}}

function toggleViewMode() {{
    const body = document.getElementById('readerBody');
    const btn = document.getElementById('viewModeBtn');
    if (currentMode === 'single') {{
        currentMode = 'continuous';
        body.className = 'mode-continuous';
        if (btn) btn.textContent = 'Mode: Scroll';
        const targetEl = document.getElementById('page-' + currentPage);
        if (targetEl) targetEl.scrollIntoView({{ behavior: 'instant' }});
    }} else {{
        currentMode = 'single';
        body.className = 'mode-single';
        if (btn) btn.textContent = 'Mode: Single';
        applyPage(currentPage);
    }}
    notifyParent();
}}

function setViewModeExplicit(mode) {{
    const body = document.getElementById('readerBody');
    const btn = document.getElementById('viewModeBtn');
    currentMode = mode === 'continuous' ? 'continuous' : 'single';
    body.className = currentMode === 'single' ? 'mode-single' : 'mode-continuous';
    if (btn) btn.textContent = currentMode === 'single' ? 'Mode: Single' : 'Mode: Scroll';
    applyPage(currentPage);
}}

function notifyParent() {{
    try {{
        if (window.parent && window.parent !== window) {{
            const targetEl = document.getElementById('page-' + currentPage);
            const chTitle = targetEl ? (targetEl.querySelector('.header-chapter')?.textContent || '') : '';
            window.parent.postMessage({{
                type: 'READER_PAGE_CHANGE',
                currentPage: currentPage,
                totalPages: TOTAL_PAGES,
                mode: currentMode,
                chapter: chTitle
            }}, '*');
        }}
    }} catch(e) {{}}
}}

window.addEventListener('message', function(event) {{
    const data = event.data;
    if (!data) return;
    if (data.action === 'GOTO_PAGE') {{
        applyPage(parseInt(data.page));
    }} else if (data.action === 'SET_MODE') {{
        setViewModeExplicit(data.mode);
    }} else if (data.action === 'NEXT_PAGE') {{
        gotoNextPage();
    }} else if (data.action === 'PREV_PAGE') {{
        gotoPrevPage();
    }}
}});

document.addEventListener('keydown', function(e) {{
    if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {{
        e.preventDefault();
        gotoNextPage();
    }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
        e.preventDefault();
        gotoPrevPage();
    }} else if (e.key === 'Home') {{
        e.preventDefault();
        applyPage(1);
    }} else if (e.key === 'End') {{
        e.preventDefault();
        applyPage(TOTAL_PAGES);
    }}
}});

let touchStartX = 0;
document.addEventListener('touchstart', function(e) {{
    touchStartX = e.changedTouches[0].screenX;
}}, {{ passive: true }});

document.addEventListener('touchend', function(e) {{
    const touchEndX = e.changedTouches[0].screenX;
    const diff = touchEndX - touchStartX;
    if (diff < -50) {{
        gotoNextPage();
    }} else if (diff > 50) {{
        gotoPrevPage();
    }}
}}, {{ passive: true }});

window.jumpToPage = function(p) {{
    applyPage(p);
}};

document.addEventListener('DOMContentLoaded', initReader);
</script>

</body>
</html>"""
        return full_html, total_pages
