#!/usr/bin/env python3
"""
Script de prueba: Verifica conexión a Cloudflare Worker
y que todo el pipeline está funcionando.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from async_client import AsyncDataPipeline
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


async def test_worker():
    """Prueba la conexión al Worker."""
    logger.info("🔍 Test: Conexión a Cloudflare Worker")
    logger.info("-" * 60)
    
    pipeline = AsyncDataPipeline()
    
    test_payload = {
        "test": True,
        "message": "Test de conexión desde Azahel",
        "gflops": 1.14,
        "device": "cpu",
    }
    
    try:
        response = await pipeline.send_data(test_payload)
        
        if response.get("status") == "success":
            logger.info("✅ ÉXITO: Worker está operativo")
            logger.info(f"   Transaction ID: {response.get('id')}")
            logger.info(f"   Hash: {response.get('hash')}")
            logger.info(f"   Message: {response.get('message')}")
            return True
        else:
            logger.error(f"❌ ERROR: {response.get('error')}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Conexión fallida: {e}")
        logger.info(
            "\n⚠️  Asegúrate de que:\n"
            "  1. Tu CLOUDFLARE_WORKER_URL en .env sea correcta\n"
            "  2. El Worker esté deployado en Cloudflare\n"
            "  3. Tengas conexión a internet"
        )
        return False
    
    finally:
        await pipeline.close()


if __name__ == "__main__":
    success = asyncio.run(test_worker())
    sys.exit(0 if success else 1)
