#!/usr/bin/env python3
"""
Simple monitoring dashboard for system health.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import requests
from backend.utils import get_logger

logger = get_logger(__name__)

API_URL = "http://localhost:8000"


def get_health():
    """Get system health."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None


def get_stats():
    """Get system stats."""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None


def display_dashboard():
    """Display monitoring dashboard."""
    while True:
        # Clear screen (works on Unix/Linux/Mac)
        print("\033[2J\033[H")
        
        print("=" * 60)
        print("🖥️  CODEBASE RAG - MONITORING DASHBOARD")
        print("=" * 60)
        print()
        
        # Health check
        health = get_health()
        if health:
            print(f"✅ Status: {health['status'].upper()}")
            print(f"📦 Version: {health['version']}")
            print()
            
            # Index stats
            stats = health.get('index_stats', {})
            print("📊 Index Statistics:")
            print(f"   Vectors: {stats.get('total_vectors', 0):,}")
            print(f"   Dimension: {stats.get('dimension', 0)}")
            print()
        else:
            print("❌ API Server: OFFLINE")
            print()
        
        # System stats
        sys_stats = get_stats()
        if sys_stats:
            print("⚙️  System Status:")
            print(f"   Status: {sys_stats.get('status', 'unknown')}")
            print(f"   Indexed: {sys_stats.get('indexed_vectors', 0):,} vectors")
            print()
        
        print("=" * 60)
        print(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Press Ctrl+C to exit")
        print("=" * 60)
        
        # Update every 5 seconds
        time.sleep(5)


if __name__ == "__main__":
    try:
        display_dashboard()
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard closed")
