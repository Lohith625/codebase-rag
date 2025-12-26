"""
Caching System
Cache query results and embeddings for faster responses.
"""

import hashlib
import pickle
from pathlib import Path
from typing import Optional, Any
from datetime import datetime, timedelta
from backend.utils import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Simple disk-based cache manager."""
    
    def __init__(self, cache_dir: Path, ttl_hours: int = 24):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache storage
            ttl_hours: Time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        logger.info(f"CacheManager initialized (TTL: {ttl_hours}h)")
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path."""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if expired/not found
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            # Check if expired
            if datetime.now() - data['timestamp'] > self.ttl:
                logger.debug(f"Cache expired: {key[:30]}...")
                cache_path.unlink()
                return None
            
            logger.debug(f"Cache hit: {key[:30]}...")
            return data['value']
        
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None
    
    def set(self, key: str, value: Any):
        """
        Set cache value.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                'value': value,
                'timestamp': datetime.now()
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug(f"Cached: {key[:30]}...")
        
        except Exception as e:
            logger.error(f"Cache write error: {e}")
    
    def clear(self):
        """Clear all cache."""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        logger.info("Cache cleared")
    
    def get_stats(self):
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_files': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }
