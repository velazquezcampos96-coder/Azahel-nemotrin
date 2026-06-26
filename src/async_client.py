#!/usr/bin/env python3
"""
Async HTTP Client para comunicación Celular ↔ Cloudflare Workers
Usa aiohttp para non-blocking I/O.
"""

import aiohttp
import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class AsyncDataPipeline:
    """Pipeline asíncrono para envío de datos a Cloudflare."""
    
    def __init__(self, worker_url: Optional[str] = None, timeout: int = 30, retry_attempts: int = 3):
        self.worker_url = worker_url or os.getenv(
            'CLOUDFLARE_WORKER_URL',
            'https://azahel.your-domain.workers.dev/api/v1/process'
        )
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"✓ AsyncDataPipeline initialized")
        logger.info(f"  Worker URL: {self.worker_url}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene o crea sesión aiohttp."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """Genera firma SHA256 del payload para integridad."""
        payload_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()
    
    async def send_data(self, data: Dict[str, Any], attempt: int = 1) -> Dict[str, Any]:
        """
        Envia datos a Cloudflare Worker con reintentos automáticos.
        
        Args:
            data: Diccionario con datos a enviar
            attempt: Número de intento actual
        
        Returns:
            Respuesta del Worker
        """
        try:
            session = await self._get_session()
            
            # Preparar payload
            payload = {
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "signature": self._generate_signature(data)
            }
            
            logger.info(f"📤 [Intento {attempt}/{self.retry_attempts}] Enviando a {self.worker_url}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Headers
            headers = {
                "Content-Type": "application/json",
                "X-Client-Version": "azahel-v2.0",
                "X-Signature": payload["signature"]
            }
            
            # POST request
            async with session.post(
                self.worker_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    logger.info(f"✓ Respuesta exitosa (status={response.status})")
                    logger.debug(f"Response: {json.dumps(response_data, indent=2)}")
                    return response_data
                
                elif response.status >= 500 and attempt < self.retry_attempts:
                    # Reintentar en errores del servidor
                    logger.warning(f"⚠️  Error del servidor (status={response.status}). Reintentando...")
                    await asyncio.sleep(2 ** (attempt - 1))  # Exponential backoff
                    return await self.send_data(data, attempt + 1)
                
                else:
                    logger.error(f"❌ Error en respuesta (status={response.status}): {response_data}")
                    return {
                        "status": "error",
                        "http_status": response.status,
                        "error": response_data
                    }
        
        except asyncio.TimeoutError:
            logger.warning(f"⏱️  Timeout en intento {attempt}. Reintentando...")
            if attempt < self.retry_attempts:
                await asyncio.sleep(2 ** (attempt - 1))
                return await self.send_data(data, attempt + 1)
            else:
                logger.error(f"❌ Falló después de {self.retry_attempts} intentos (Timeout)")
                return {"status": "error", "error": "timeout"}
        
        except aiohttp.ClientError as e:
            logger.warning(f"🌐 Error de conexión en intento {attempt}: {e}")
            if attempt < self.retry_attempts:
                await asyncio.sleep(2 ** (attempt - 1))
                return await self.send_data(data, attempt + 1)
            else:
                logger.error(f"❌ Falló después de {self.retry_attempts} intentos (Network Error)")
                return {"status": "error", "error": str(e)}
        
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    async def close(self):
        """Cierra la sesión aiohttp."""
        if self.session:
            await self.session.close()
            logger.info("✓ Session cerrada")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def test_connection():
    """Test rápido de conexión al Worker."""
    logger.info("🧪 Probando conexión a Cloudflare Worker...")
    
    pipeline = AsyncDataPipeline()
    test_data = {
        "test": True,
        "message": "Conexión de prueba desde Azahel",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        response = await pipeline.send_data(test_data)
        logger.info(f"✓ Conexión exitosa")
        logger.info(f"Response: {json.dumps(response, indent=2)}")
    finally:
        await pipeline.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    asyncio.run(test_connection())
