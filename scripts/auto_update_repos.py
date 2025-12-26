#!/usr/bin/env python3
"""
Auto-update indexed repositories.
Pull latest changes from all indexed repositories.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ingestion.github_loader import GitHubLoader
from backend.utils import get_logger
from config.settings import settings

logger = get_logger(__name__)


def update_repositories():
    """Update all indexed repositories."""
    logger.info("Starting repository auto-update...")
    
    loader = GitHubLoader()
    repos_path = settings.repositories_path
    
    if not repos_path.exists():
        logger.warning("No repositories directory found")
        return
    
    updated = 0
    failed = 0
    
    # Iterate through all cloned repositories
    for repo_dir in repos_path.iterdir():
        if repo_dir.is_dir() and (repo_dir / ".git").exists():
            logger.info(f"Updating {repo_dir.name}...")
            
            try:
                success = loader.pull_latest(repo_dir)
                if success:
                    updated += 1
                    logger.info(f"✅ Updated {repo_dir.name}")
                else:
                    failed += 1
                    logger.warning(f"⚠️ Failed to update {repo_dir.name}")
            except Exception as e:
                failed += 1
                logger.error(f"❌ Error updating {repo_dir.name}: {e}")
    
    logger.info(f"Auto-update complete: {updated} updated, {failed} failed")


if __name__ == "__main__":
    update_repositories()
