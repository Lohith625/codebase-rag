#!/usr/bin/env python3
"""Test all API connections."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from backend.utils import get_logger

logger = get_logger(__name__)


def test_gemini():
    """Test Gemini API connection."""
    if not settings.gemini_api_key:
        logger.warning("⚠️  Gemini API key not set in .env")
        return False

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)

        # Use the correct model name for Gemini
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say 'Hello from Gemini!'")
        logger.info(f"✅ Gemini API: {response.text.strip()}")
        return True
    except Exception as e:
        logger.error(f"❌ Gemini API failed: {e}")
        logger.info(
            "   Tip: Make sure you're using a valid Gemini API key from https://makersuite.google.com/app/apikey"
        )
        return False


def test_openai():
    """Test OpenAI API connection."""
    if not settings.openai_api_key:
        logger.warning("⚠️  OpenAI API key not set in .env")
        return False

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=settings.openai_api_key, timeout=30.0  # Increased timeout
        )
        response = client.embeddings.create(
            model="text-embedding-ada-002", input="Hello OpenAI"
        )
        logger.info(
            f"✅ OpenAI API: Connected (embedding dimension: {len(response.data[0].embedding)})"
        )
        return True
    except Exception as e:
        logger.error(f"❌ OpenAI API failed: {e}")
        logger.info(
            "   Tip: Check your OpenAI API key at https://platform.openai.com/api-keys"
        )
        return False


def test_pinecone():
    """Test Pinecone API connection."""
    if not settings.pinecone_api_key:
        logger.warning("⚠️  Pinecone API key not set in .env")
        return False

    try:
        from pinecone import Pinecone

        pc = Pinecone(api_key=settings.pinecone_api_key)
        indexes = pc.list_indexes()
        logger.info(
            f"✅ Pinecone API: Connected (environment: {settings.pinecone_environment})"
        )
        logger.info(f"   Available indexes: {[idx.name for idx in indexes]}")
        return True
    except Exception as e:
        logger.error(f"❌ Pinecone API failed: {e}")
        return False


def main():
    logger.info("🚀 Testing API connections...")
    logger.info("=" * 60)

    results = {
        "Gemini": test_gemini(),
        "OpenAI": test_openai(),
        "Pinecone": test_pinecone(),
    }

    logger.info("\n" + "=" * 60)
    logger.info("📊 Summary:")
    for api, status in results.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {api}: {'Connected' if status else 'Failed'}")

    # Check if at least one LLM is working
    llm_working = results["Gemini"] or results["OpenAI"]

    if llm_working and results["Pinecone"]:
        logger.info(
            "\n✅ You have at least one LLM and Pinecone working! You're ready to go!"
        )
        logger.info("\n🎯 Next: Start Phase 2 - Data Ingestion Pipeline")
        return 0
    elif llm_working:
        logger.info("\n✅ You have at least one LLM working!")
        logger.info("   We'll use FAISS instead of Pinecone (no problem!)")
        logger.info("\n🎯 Next: Start Phase 2 - Data Ingestion Pipeline")
        return 0
    else:
        logger.error("\n❌ No LLM API working. Please check your API keys.")
        logger.info("   You need at least one of: Gemini or OpenAI")
        return 1


if __name__ == "__main__":
    sys.exit(main())
