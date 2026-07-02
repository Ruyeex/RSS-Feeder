"""Main entry point for RSS Feed Generator."""

import sys
import os
from src.config import FEED_FILE, NUM_ITEMS, GIT_USER_NAME, GIT_USER_EMAIL, GIT_BRANCH
from src.logger import setup_logger
from src.api import fetch_mods
from src.rss_builder import build_rss
from src.git_handler import setup_git, commit_and_push

logger = setup_logger(__name__)


def main():
    """Main entry point for RSS feed generation."""
    try:
        logger.info("Starting RSS feed generation...")
        
        # Fetch mods
        mods = fetch_mods(NUM_ITEMS)
        if not mods:
            logger.error("No mods returned from API")
            sys.exit(1)
        
        # Build RSS feed
        logger.info(f"Building RSS feed with {len(mods)} items...")
        rss = build_rss(mods)
        
        # Write feed to file
        try:
            os.makedirs(os.path.dirname(FEED_FILE) or ".", exist_ok=True)
            with open(FEED_FILE, "w", encoding="utf-8") as f:
                f.write(rss)
            logger.info(f"✓ Successfully wrote {len(mods)} items to {FEED_FILE}")
        except IOError as e:
            logger.error(f"Error writing RSS feed: {e}")
            sys.exit(1)
        
        # Setup git and commit/push if needed
        if os.getenv("GITHUB_ACTIONS") == "true":
            logger.info("Running in GitHub Actions environment")
            setup_git(GIT_USER_NAME, GIT_USER_EMAIL)
            commit_and_push(FEED_FILE, GIT_BRANCH)
        else:
            logger.info("Not running in GitHub Actions, skipping git operations")
        
        logger.info("✓ RSS feed generation completed successfully")
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
