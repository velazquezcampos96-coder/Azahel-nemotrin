#!/usr/bin/env python3
"""
AZAHEL NEMOTRON - PyTorch Local Processor (KPKAVE v2.5)
Procesa matrices a velocidad nativa del celular (1.14 GFLOPS)
y envia resultados a Cloudflare Worker con contrato de datos optimizado.
"""

import torch
import time
import json
import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
import sys
import platform

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from async_client import AsyncDataPipeline

# Configurar logging con mejor formato
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class AzaelProcessor:
    """Procesador PyTorch para Azahel Nemotrin KPKAVE v2.5"""
    
    def __init__(self, matrix_size=None, worker_url=None):
        # Leer configuración desde .env
        self.matrix_size = matrix_size or int(os.getenv('PYTORCH_MATRIX_SIZE', 1000))
        self.worker_url = worker_url or os.getenv('CLOUDFLARE_WORKER_URL')
        self.device = torch.device('cpu')  # Celular usa CPU
        self.pipeline = AsyncDataPipeline(worker_url=self.worker_url)
        
        # Detectar dispositivo
        self.device_name = self._detect_device()
        
        logger.info(f"✓ Azahel Processor initialized")
        logger.info(f"  Device: {self.device_name}")
        logger.info(f"  PyTorch: {torch.__version__}")
        logger.info(f"  Matrix Size: {self.matrix_size}x{self.matrix_size}")
        logger.info(f"  Worker URL: {self.worker_url}")
    
    def _detect_device(self) -> str:
        """Detecta nombre del dispositivo y SO."""
        system = platform.system()
        machine = platform.machine()
        
        # Detectar si es Termux
        if os.path.exists('/data/data/com.termux'):
            return f"Termux-{system}-{machine}"
        
        return f"{system}-{machine}"
    
    def process_matrix(self) -> dict:
        """
        Procesa matriz y calcula GFLOPS.
        Retorna dict con métricas en formato KPKAVE v2.5.
        """
        logger.info(f"🔥 Iniciando procesamiento matriz {self.matrix_size}x{self.matrix_size}")
        logger.info(f"   Dispositivo: {self.device_name}")
        
        try:
            # Generar matrices aleatorias
            start_gen = time.time()
            A = torch.randn(self.matrix_size, self.matrix_size, device=self.device)
            B = torch.randn(self.matrix_size, self.matrix_size, device=self.device)
            tiempo_generacion = time.time() - start_gen
            
            logger.info(f"✓ Matrices generadas en {tiempo_generacion:.4f}s")
            
            # Realizar multiplicación matricial (operación crítica)
            process_start = time.time()
            C = torch.matmul(A, B)
            elapsed = time.time() - process_start
            
            # Calcular GFLOPS
            # Multiplicación matricial: 2 * N^3 operaciones floating point
            flops = 2 * (self.matrix_size ** 3)
            gflops = (flops / elapsed) / 1e9
            
            logger.info(f"✓ Multiplicación completada en {elapsed:.4f}s")
            logger.info(f"📊 GFLOPS: {gflops:.4f}")
            logger.info(f"📊 Total FLOPS: {flops:,}")
            
            # Contrato de datos KPKAVE v2.5 (lo que espera el edge bunker)
            result = {
                "gflops": round(gflops, 4),  # Métrica principal
                "tiempo_procesamiento": round(elapsed, 4),  # Segundos de ejecución
                "dispositivo": self.device_name,  # Identificación del device
                # Metadata adicional (opcional pero útil)
                "matrix_size": self.matrix_size,
                "total_flops": int(flops),
                "timestamp_local": datetime.utcnow().isoformat(),
                "device_torch": str(self.device),
                "pytorch_version": torch.__version__,
                "matrix_stats": {
                    "suma": float(C.sum().item()),
                    "media": float(C.mean().item()),
                    "desv_std": float(C.std().item())
                }
            }
            
            logger.info(f"✓ Contrato KPKAVE v2.5 generado")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento: {e}", exc_info=True)
            raise
    
    async def send_to_cloudflare(self, data: dict) -> dict:
        """
        Envia datos procesados a Cloudflare Worker via AsyncDataPipeline.
        Utiliza el contrato KPKAVE v2.5.
        """
        logger.info(f"📤 Enviando a BÚNKER DE BORDE KPKAVE v2.5...")
        logger.debug(f"   Payload: {json.dumps(data, indent=2)}")
        
        try:
            response = await self.pipeline.send_data(data)
            
            if response.get('status') == 'error':
                logger.error(f"❌ Error en respuesta del Worker: {response.get('error')}")
            else:
                logger.info(f"✓ Respuesta recibida del Worker")
                if 'meta' in response:
                    txn_id = response['meta'].get('transactionId')
                    logger.info(f"   Transaction ID: {txn_id}")
                    logger.info(f"   Status: {response['meta'].get('status')}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error al enviar: {e}", exc_info=True)
            raise
    
    async def run_pipeline(self):
        """
        Ejecuta el pipeline completo:
        1. Procesa matriz localmente
        2. Empaqueta en contrato KPKAVE v2.5
        3. Envia a Cloudflare Worker
        4. Recibe confirmación
        """
        logger.info("="*70)
        logger.info("🔮 AZAHEL NEMOTRON - PIPELINE KPKAVE v2.5 INTEGRADO")
        logger.info("="*70)
        
        try:
            # Paso 1: Procesamiento local
            logger.info("\n[PASO 1] Procesamiento Local")
            logger.info("-" * 70)
            local_result = self.process_matrix()
            
            # Paso 2: Envío a Cloudflare (contrato KPKAVE v2.5)
            logger.info("\n[PASO 2] Transmisión a Edge")
            logger.info("-" * 70)
            cloudflare_response = await self.send_to_cloudflare(local_result)
            
            # Paso 3: Consolidar resultados finales
            logger.info("\n[PASO 3] Consolidación")
            logger.info("-" * 70)
            
            final_output = {
                "status": "success",
                "timestamp_inicio": datetime.utcnow().isoformat(),
                "local_processing": local_result,
                "cloudflare_response": cloudflare_response,
                "pipeline_version": "KPKAVE-v2.5"
            }
            
            logger.info("\n" + "="*70)
            logger.info("✅ PIPELINE COMPLETADO EXITOSAMENTE")
            logger.info("="*70)
            logger.info(f"\nResultado Final:")
            logger.info(json.dumps(final_output, indent=2))
            logger.info("\n" + "="*70 + "\n")
            
            return final_output
            
        except Exception as e:
            logger.error(f"\n❌ PIPELINE FALLIDO: {e}", exc_info=True)
            raise


async def main():
    """Punto de entrada del pipeline."""
    # Validar configuración
    worker_url = os.getenv('CLOUDFLARE_WORKER_URL')
    if not worker_url:
        logger.error("❌ ERROR: CLOUDFLARE_WORKER_URL no configurada en .env")
        logger.error("   Edita .env y configura tu URL del Worker")
        sys.exit(1)
    
    processor = AzaelProcessor()
    await processor.run_pipeline()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️  Pipeline interrumpido por usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline error fatal: {e}", exc_info=True)
        sys.exit(1)
