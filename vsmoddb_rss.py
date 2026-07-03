"""
Generates an RSS feed of the newest Vintage Story mod updates,
using the official Mod DB API: https://github.com/anegostudios/vsmoddb
Usage:
    pip install requests
    python vsmoddb_rss.py
Output:
    vsmoddb_updates.xml  (an RSS 2.0 feed you can subscribe to / host anywhere)
To keep the feed current, run this on a schedule (cron, GitHub Action, etc.)
and serve the resulting XML file from a static host.
"""
import requests
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape
import os
API_URL = "https://mods.vintagestory.at/api/mods"
SITE_BASE = "https://mods.vintagestory.at/"
FEED_FILE = "vsmoddb_updates.xml"
NUM_ITEMS = 30  # how many of the most recently updated mods to include
def fetch_mods():
    params = {
        "orderby": "lastreleased",
        "orderdirection": "desc",
    }
    resp = requests.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # The API wraps results in a "mods" list alongside a statuscode field
    mods = data.get("mods") or data.get("data") or []
    return mods[:NUM_ITEMS]
def parse_date(value):
    """The API's lastreleased field has shown up as either an ISO string
    or a unix timestamp depending on version, so handle both."""
    if value is None:
        return datetime.now(timezone.utc)
    try:
        if isinstance(value, (int, float)) or str(value).isdigit():
            return datetime.fromtimestamp(int(value), tz=timezone.utc)
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return datetime.now(timezone.utc)
def mod_link(mod):
    slug = mod.get("urlalias") or mod.get("modid") or mod.get("assetid")
    return f"{SITE_BASE}show/mod/{slug}" if slug else SITE_BASE
def safe_escape(text):
    """Safely escape text for XML, handling special characters"""
    if text is None:
        return ""
    # Convert to string and escape XML special characters
    return escape(str(text))
def build_rss(mods):
    items_xml = []
    for mod in mods:
        name = safe_escape(mod.get("name", "Unknown mod"))
        summary = safe_escape(mod.get("summary") or mod.get("text") or "")
        link = safe_escape(mod_link(mod))
        pub_date = format_datetime(parse_date(mod.get("lastreleased")))
        
        # Use modid/assetid for GUID instead of lastreleased
        # This avoids issues with special characters in timestamps
        mod_id = mod.get("modid") or mod.get("assetid") or ""
        guid = safe_escape(f"{link}#{mod_id}")
        
        items_xml.append(f"""  <item>
    <title>{name}</title>
    <link>{link}</link>
    <guid isPermaLink="false">{guid}</guid>
    <pubDate>{pub_date}</pubDate>
    <description>{summary}</description>
  </item>""")
    
    now = format_datetime(datetime.now(timezone.utc))
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Vintage Story Mod DB - Latest Updates</title>
  <link>{safe_escape(SITE_BASE)}</link>
  <description>Newest mod releases and updates from the Vintage Story Mod DB</description>
  <lastBuildDate>{now}</lastBuildDate>
{chr(10).join(items_xml)}
</channel>
</rss>
"""
    return rss
def main():
    mods = fetch_mods()
    if not mods:
        print("No mods returned - check the API response structure (data.get('mods')).")
        return
    
    rss = build_rss(mods)
    
    # Write new file (overwrites existing file automatically)
    with open(FEED_FILE, "w", encoding="utf-8") as f:
        f.write(rss)
    print(f"Wrote {len(mods)} items to {FEED_FILE}")
if __name__ == "__main__":
    main()
