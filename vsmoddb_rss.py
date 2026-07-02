"""
Vintage Story Mod DB RSS Feed Generator

Fetches the latest mods from the Vintage Story Mod DB API
and generates an RSS feed for easy subscription to mod updates.
"""

import requests
import sys
import logging
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape
from typing import List, Dict, Optional
from pathlib import Path

# Configuration
API_URL = "https://mods.vintagestory.at/api/mods"
SITE_BASE = "https://mods.vintagestory.at/"
FEED_FILE = "vsmoddb_updates.xml"
NUM_ITEMS = 30
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_mods() -> List[Dict]:
    """
    Fetch latest mods from Vintage Story Mod DB API with retries.
    
    Returns:
        List of mod dictionaries, up to NUM_ITEMS
    """
    params = {"orderby": "lastreleased", "orderdirection": "desc"}
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetching mods from API (attempt {attempt}/{MAX_RETRIES})...")
            resp = requests.get(
                API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
                headers={"User-Agent": "VSModDBRSSFeeder/1.0"}
            )
            resp.raise_for_status()
            
            data = resp.json()
            
            # Try multiple possible keys for the mods list
            mods = data.get("mods") or data.get("data") or []
            
            if not isinstance(mods, list):
                logger.warning(f"Unexpected mods format: {type(mods)}")
                mods = []
            
            logger.info(f"Successfully fetched {len(mods)} mods from API")
            return mods[:NUM_ITEMS]
            
        except requests.Timeout:
            logger.warning(f"Request timeout on attempt {attempt}/{MAX_RETRIES}")
            if attempt == MAX_RETRIES:
                logger.error("Failed to fetch mods after maximum retries")
                return []
                
        except requests.ConnectionError as e:
            logger.warning(f"Connection error on attempt {attempt}/{MAX_RETRIES}: {e}")
            if attempt == MAX_RETRIES:
                logger.error("Failed to connect to API after maximum retries")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Request failed on attempt {attempt}/{MAX_RETRIES}: {e}")
            if attempt == MAX_RETRIES:
                return []
                
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return []
    
    return []


def parse_date(value: Optional[str]) -> datetime:
    """
    Parse various date formats to datetime object.
    
    Handles:
    - Unix timestamps (int/float)
    - ISO 8601 strings
    - None values (defaults to current UTC time)
    
    Args:
        value: Date value in various formats
        
    Returns:
        datetime object in UTC timezone
    """
    if value is None:
        return datetime.now(timezone.utc)
    
    try:
        value_str = str(value).strip()
        
        # Try parsing as Unix timestamp
        if value_str.replace('.', '', 1).replace('-', '', 1).isdigit():
            return datetime.fromtimestamp(float(value_str), tz=timezone.utc)
        
        # Try ISO format
        value_str = value_str.replace("Z", "+00:00")
        return datetime.fromisoformat(value_str)
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Failed to parse date '{value}': {e}. Using current UTC time.")
        return datetime.now(timezone.utc)


def get_mod_link(mod: Dict) -> str:
    """
    Generate mod link from mod data.
    
    Tries multiple fields to construct a valid URL.
    
    Args:
        mod: Mod data dictionary
        
    Returns:
        URL string for the mod
    """
    slug = mod.get("urlalias") or mod.get("modid") or mod.get("assetid")
    if slug:
        return f"{SITE_BASE}show/mod/{slug}"
    return SITE_BASE


def validate_mod(mod: Dict) -> bool:
    """
    Validate that a mod has minimum required fields.
    
    Args:
        mod: Mod data dictionary
        
    Returns:
        True if mod is valid, False otherwise
    """
    if not isinstance(mod, dict):
        return False
    
    name = mod.get("name", "").strip()
    has_link = bool(mod.get("urlalias") or mod.get("modid") or mod.get("assetid"))
    
    return bool(name) and has_link


def build_rss(mods: List[Dict]) -> str:
    """
    Build RSS feed from mod data.
    
    Args:
        mods: List of mod dictionaries
        
    Returns:
        RSS XML string
    """
    items_xml = []
    valid_mod_count = 0
    
    for i, mod in enumerate(mods, 1):
        try:
            if not validate_mod(mod):
                logger.debug(f"Skipping invalid mod #{i}")
                continue
            
            name = escape(str(mod.get("name", "Unknown mod")).strip())
            summary = escape(str(mod.get("summary") or mod.get("text") or "").strip())
            link = escape(get_mod_link(mod))
            pub_date = format_datetime(parse_date(mod.get("lastreleased")))
            guid = escape(f"{link}#{mod.get('lastreleased', 'unknown')}")
            
            items_xml.append(f"""  <item>
    <title>{name}</title>
    <link>{link}</link>
    <guid isPermaLink="false">{guid}</guid>
    <pubDate>{pub_date}</pubDate>
    <description>{summary}</description>
  </item>""")
            
            valid_mod_count += 1
            
        except Exception as e:
            logger.warning(f"Error processing mod #{i}: {e}")
            continue
    
    if not items_xml:
        logger.warning("No valid mods to include in RSS feed")
    
    now = format_datetime(datetime.now(timezone.utc))
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel>
  <title>Vintage Story Mod DB - Latest Updates</title>
  <link>{SITE_BASE}</link>
  <description>Newest mod releases and updates from the Vintage Story Mod DB</description>
  <lastBuildDate>{now}</lastBuildDate>
  <generator>VSModDBRSSFeeder/1.0</generator>
{chr(10).join(items_xml)}
</channel>
</rss>
"""
    return rss


def write_feed(rss: str, filepath: str) -> bool:
    """
    Write RSS feed to file with error handling.
    
    Args:
        rss: RSS XML string
        filepath: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rss)
        
        file_size = output_path.stat().st_size
        logger.info(f"✓ Successfully wrote feed to {filepath} ({file_size} bytes)")
        return True
        
    except IOError as e:
        logger.error(f"Error writing RSS feed to {filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error writing feed: {e}")
        return False


def main():
    """Main entry point."""
    logger.info("Starting Vintage Story Mod DB RSS Feed Generator...")
    
    # Fetch mods
    mods = fetch_mods()
    
    if not mods:
        logger.error("No mods returned from API. Feed generation failed.")
        return 1
    
    logger.info(f"Fetched {len(mods)} mods, building RSS feed...")
    
    # Build and write RSS
    rss = build_rss(mods)
    
    if not write_feed(rss, FEED_FILE):
        return 1
    
    logger.info("✓ RSS feed generation completed successfully")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
