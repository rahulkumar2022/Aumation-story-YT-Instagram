#!/usr/bin/env python3
"""
YouTube SEO Keyword Engine for 'Pass The Salt POV'.
Sourced and verified via KeywordTool.io YouTube autocomplete intelligence:
- Queries researched: 'pov stories', 'billionaire pov', 'animated stories', 'motion comic', 'pass the salt pov'
"""

# Core high-volume search queries from KeywordTool.io
PRIMARY_SEARCH_KEYWORDS = [
    "pov stories",
    "billionaire pov",
    "animated stories",
    "motion comic",
    "pov storytime animation",
    "billionaire in disguise",
    "billionaire family pov",
    "pass the salt pov",
    "from poverty to billionaire",
    "rich vs poor",
    "dramatic pov stories",
    "life lessons story",
    "quiet wealth",
    "stealth wealth",
    "instant karma",
]

# Curated top 10 keywords explicitly embedded in video descriptions
DESCRIPTION_KEYWORDS = [
    "pov stories",
    "billionaire pov",
    "animated stories",
    "motion comic",
    "billionaire in disguise",
    "billionaire family pov",
    "pass the salt pov",
    "rich vs poor",
    "stealth wealth",
    "life lessons story",
]

# Curated tags for YouTube upload metadata
RECOMMENDED_TAGS_SHORTS = [
    "pov stories",
    "billionaire pov",
    "animated stories",
    "motion comic",
    "pov storytime animation",
    "billionaire family pov",
    "billionaire in disguise",
    "rich vs poor",
    "pass the salt pov",
    "dramatic pov stories",
    "animated pov",
    "life lessons story",
    "quiet wealth",
    "shorts",
    "storytime"
]

RECOMMENDED_TAGS_LONG = [
    "pov stories",
    "billionaire pov",
    "animated stories",
    "motion comic",
    "pov storytime animation",
    "billionaire family pov",
    "billionaire in disguise",
    "rich vs poor",
    "pass the salt pov",
    "dramatic pov stories",
    "life lessons story",
    "quiet wealth",
    "stealth wealth",
    "motion comic dub",
    "2d animation story",
    "webtoon animation",
    "full story"
]

# Verified high-traction YouTube hashtags
HASHTAGS_SHORTS = [
    "#pov",
    "#povstories",
    "#billionairepov",
    "#motioncomic",
    "#animatedstories",
    "#storytime",
    "#animation",
    "#drama",
    "#lifelessons",
    "#richvspoor",
    "#shorts"
]

HASHTAGS_LONG = [
    "#pov",
    "#povstories",
    "#billionairepov",
    "#motioncomic",
    "#animatedstories",
    "#storytime",
    "#animation",
    "#drama",
    "#lifelessons",
    "#richvspoor",
    "#fullstory"
]

# High-CTR title formulas identified from autocomplete rankings
TITLE_TEMPLATES = [
    "POV: The {underestimated_role} Is Actually The Billionaire {secret_role} (Motion Comic)",
    "POV: 'Pass The Salt' — When Your Toxic Billionaire Family Realizes Who You Are",
    "POV: You're The Billionaire In Disguise Working Minimum Wage (Full Story)",
    "POV: You Belong To A Billionaire Family... But They Forgot You Own The Company",
    "From Poverty To Billionaire: The Ultimate Life Lesson (Animated Drama)",
]

def format_title(title: str, is_short: bool = True) -> str:
    """
    Cleans and formats a video title for maximum CTR and YouTube SEO.
    - Ensures 'POV:' or 'POV' is prominent if applicable.
    - Appends #Shorts for vertical format if not already present.
    - Keeps within YouTube's 100-character limit.
    """
    title = title.strip()
    if is_short:
        if "#Shorts" not in title and "#shorts" not in title.lower():
            # If title + ' #Shorts' exceeds 100 chars, truncate title safely
            max_len = 92
            if len(title) > max_len:
                title = title[:max_len].rstrip()
            title = f"{title} #Shorts"
    else:
        # Long-form title limit is 100 chars
        if len(title) > 100:
            title = title[:97].rstrip() + "..."
    return title

def format_description(base_summary: str, is_short: bool = True, extra_context: str = "") -> str:
    """
    Builds an SEO-optimized description containing:
    1. Narrative hook / summary
    2. Channel CTA
    3. Keyword search queries block (for algorithm indexing)
    4. Verified trending hashtags
    """
    summary = base_summary.strip()
    
    # Clean existing trailing hashtags from base summary to avoid duplication
    words = [w for w in summary.split() if not w.startswith("#")]
    clean_summary = " ".join(words)

    channel_cta = (
        "🔔 Subscribe to Pass The Salt POV (@PassTheSaltPOV) for daily 2D graphic novel "
        "motion comics, subtle wealth parables, and quiet karma animated stories."
    )

    keyword_bullets = "\n".join(f"• {kw.title()}" for kw in DESCRIPTION_KEYWORDS)
    keywords_cloud = ", ".join(DESCRIPTION_KEYWORDS)

    keyword_block = (
        "🔍 Topics & Search Queries:\n"
        f"{keyword_bullets}\n\n"
        f"🏷️ Related Keywords: {keywords_cloud}"
    )

    hashtags = " ".join(HASHTAGS_SHORTS if is_short else HASHTAGS_LONG)

    sections = [clean_summary]
    if extra_context:
        sections.append(extra_context.strip())
    sections.append(channel_cta)
    sections.append(keyword_block)
    sections.append(hashtags)

    return "\n\n".join(sections)

def enrich_tags(existing_tags: list = None, mode: str = "short") -> list:
    """
    Combines custom/AI tags with the highest-ranking KeywordTool.io keywords.
    Deduplicates while preserving order and respecting YouTube's limits.
    """
    base_set = RECOMMENDED_TAGS_SHORTS if mode == "short" else RECOMMENDED_TAGS_LONG
    combined = []
    seen = set()

    for tag in (existing_tags or []) + base_set:
        cleaned = tag.strip().lower()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            combined.append(tag.strip())

    return combined[:20]
