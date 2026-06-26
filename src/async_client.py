#!/usr/bin/env python3
"""
Async HTTP Client para comunicación Celular ↔ Cloudflare Workers (KPKAVE v2.5)
Usa aiohttp para non-blocking I/O con reintentos inteligentes.
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
    """Pipeline asíncrono para envío de datos a Cloudflare Workers (KPKAVE v2.5)"""
    
    def __init__(self, worker_url: Optional[str] = None, timeout: int = 30, retry_attempts: int = 3):
        self.worker_url = worker_url or os.getenv(
            'CLOUDFLARE_WORKER_URL',
            'https://azahel.your-domain.workers.dev/api/v1/process'
        )
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"✓ AsyncDataPipeline (KPKAVE v2.5) initialized")
        logger.info(f"  Worker URL: {self.worker_url}")
        logger.info(f"  Timeout: {timeout}s | Reintentos: {retry_attempts}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene o crea sesión aiohttp reutilizable."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """Genera firma SHA256 del payload para integridad (KPKAVE)."""
        payload_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()
    
    async def send_data(self, data: Dict[str, Any], attempt: int = 1) -> Dict[str, Any]:
        """
        Envia datos a Cloudflare Worker con reintentos automáticos.
        Contrato KPKAVE v2.5: gflops, tiempo_procesamiento, dispositivo
        
        Args:
            data: Diccionario con datos a enviar (debe contener gflops, tiempo_procesamiento, dispositivo)
            attempt: Número de intento actual
        
        Returns:
            Respuesta del Worker con estructura KPKAVE v2.5
        """
        try:
            session = await self._get_session()
            
            # Validar contrato mínimo
            required_fields = ['gflops', 'tiempo_procesamiento', 'dispositivo']
            missing = [f for f in required_fields if f not in data]
            if missing:
                logger.error(f"❌ Campos requeridos faltantes: {missing}")
                return {
                    "status": "error",
                    "error": f"Campos faltantes: {', '.join(missing)}"
                }
            
            # Preparar payload para envío
            payload = {
                "gflops": data['gflops'],
                "tiempo_procesamiento": data['tiempo_procesamiento'],
                "dispositivo": data['dispositivo'],
                # Incluir metadata adicional si existe
                **{k: v for k, v in data.items() 
                   if k not in ['gflops', 'tiempo_procesamiento', 'dispositivo']}
            }
            
            signature = self._generate_signature(payload)
            
            logger.info(f"📤 [Intento {attempt}/{self.retry_attempts}] Enviando a Worker")
            logger.debug(f"   GFLOPS: {payload['gflops']}, Tiempo: {payload['tiempo_procesamiento']}s")
            
            # Headers HTTP
            headers = {
                "Content-Type": "application/json",
                "X-Client-Version": "azahel-nemotron-v2.5",
                "X-Client-Platform": "termux-android",
                "X-Signature": signature
            }
            
            # POST request con timeout
            async with session.post(
                self.worker_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                try:
                    response_data = await response.json()
                except asyncio.TimeoutError:
                    raise asyncio.TimeoutError(f"Timeout parsing response (attempt {attempt})")
                except Exception as parse_err:
                    logger.error(f"Error parsing JSON response: {parse_err}")
                    return {
                        "status": "error",
                        "error": f"Invalid JSON response from worker: {parse_err}"
                    }
                
                if response.status == 200:
                    logger.info(f"✓ Respuesta exitosa del Worker (HTTP {response.status})")
                    logger.debug(f"   Response: {json.dumps(response_data, indent=2)}")
                    return response_data
                
                elif response.status >= 500 and attempt < self.retry_attempts:
                    # Reintentar en errores del servidor (5xx)
                    logger.warning(f"⚠️  Error del servidor (HTTP {response.status}). Reintentando...")
                    wait_time = 2 ** (attempt - 1)
                    logger.info(f"   Esperando {wait_time}s antes del siguiente intento...")
                    await asyncio.sleep(wait_time)
                    return await self.send_data(data, attempt + 1)
                
                else:
                    # Error del cliente (4xx) o máximo de reintentos alcanzado
                    logger.error(f"❌ Error en respuesta (HTTP {response.status}): {response_data}")
                    return {
                        "status": "error",
                        "http_status": response.status,
                        "error": response_data.get('error', 'Unknown error'),
                        "detalle": response_data
                    }
        
        except asyncio.TimeoutError:
            logger.warning(f"⏱️  Timeout en intento {attempt}/{self.retry_attempts}")
            if attempt < self.retry_attempts:
                wait_time = 2 ** (attempt - 1)
                logger.info(f"   Esperando {wait_time}s antes del siguiente intento...")
                await asyncio.sleep(wait_time)
                return await self.send_data(data, attempt + 1)
            else:
                logger.error(f"❌ Falló después de {self.retry_attempts} intentos (Timeout)")
                return {"status": "error", "error": "timeout", "detalle": "Connection timeout"}
        
        except aiohttp.ClientError as e:
            logger.warning(f"🌐 Error de conexión en intento {attempt}: {type(e).__name__}: {e}")
            if attempt < self.retry_attempts:
                wait_time = 2 ** (attempt - 1)
                logger.info(f"   Esperando {wait_time}s antes del siguiente intento...")
                await asyncio.sleep(wait_time)
                return await self.send_data(data, attempt + 1)
            else:
                logger.error(f"❌ Falló después de {self.retry_attempts} intentos (Network Error)")
                return {"status": "error", "error": str(e), "detalle": "Network connectivity issue"}
        
        except Exception as e:
            logger.error(f"❌ Error inesperado: {type(e).__name__}: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "detalle": "Unexpected error"}
    
    async def close(self):
        """Cierra la sesión aiohttp de forma limpia."""
        if self.session:
            await self.session.close()
            logger.info("✓ Session cerrada")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def test_connection():
    """Test rápido de conexión al Worker (para debugging)."""
    logger.info("🧪 Probando conexión a Cloudflare Worker...\n")
    
    pipeline = AsyncDataPipeline()
    
    # Datos de prueba en formato KPKAVE v2.5
    test_data = {
        "gflops": 1.14,
        "tiempo_procesamiento": 47.1643,
        "dispositivo": "Termux-Android-armv8l",
        "test": True,
        "message": "Prueba de conexión desde Azahel Nemotron"
    }
    
    try:
        response = await pipeline.send_data(test_data)
        logger.info(f"\n✓ Test completado")
        logger.info(f"Response: {json.dumps(response, indent=2)}")
    finally:
        await pipeline.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    asyncio.run(test_connection())
