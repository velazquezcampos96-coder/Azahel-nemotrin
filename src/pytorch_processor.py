#!/usr/bin/env python3
"""
Azahel Nemotrin - PyTorch Local Processor
Procesa matrices a velocidad nativa del celular (1.14 GFLOPS)
y envia resultados a Cloudflare Worker en tiempo real.
"""

import torch
import time
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from async_client import AsyncDataPipeline

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class AzaelProcessor:
    """Procesador PyTorch para Azahel Nemotrin KPKAVE v2.0"""
    
    def __init__(self, matrix_size=1000, batch_size=1000):
        self.matrix_size = matrix_size
        self.batch_size = batch_size
        self.device = torch.device('cpu')  # Celular usa CPU
        self.pipeline = AsyncDataPipeline()
        
        logger.info(f"✓ Azahel Processor initialized")
        logger.info(f"  Device: {self.device}")
        logger.info(f"  PyTorch: {torch.__version__}")
    
    def process_matrix(self):
        """
        Procesa matriz y calcula GFLOPS.
        Retorna dict con métricas.
        """
        logger.info(f"🔥 Iniciando procesamiento matriz {self.matrix_size}x{self.matrix_size}")
        
        try:
            # Generar matrices aleatorias
            start_time = time.time()
            A = torch.randn(self.matrix_size, self.matrix_size, device=self.device)
            B = torch.randn(self.matrix_size, self.matrix_size, device=self.device)
            
            logger.info(f"✓ Matrices generadas")
            
            # Realizar multiplicación matricial
            process_start = time.time()
            C = torch.matmul(A, B)
            elapsed = time.time() - process_start
            
            # Calcular GFLOPS
            # Multiplicación matricial: 2 * N^3 operaciones
            flops = 2 * (self.matrix_size ** 3)
            gflops = (flops / elapsed) / 1e9
            
            # Resultados
            result = {
                "timestamp": datetime.utcnow().isoformat(),
                "matrix_size": self.matrix_size,
                "elapsed_seconds": round(elapsed, 4),
                "total_flops": int(flops),
                "gflops": round(gflops, 4),
                "device": str(self.device),
                "matrix_sum": float(C.sum().item()),
                "matrix_mean": float(C.mean().item()),
                "matrix_std": float(C.std().item()),
            }
            
            logger.info(f"✓ Procesamiento completado en {elapsed:.4f}s")
            logger.info(f"📊 GFLOPS: {gflops:.4f}")
            logger.info(f"📊 Total FLOPS: {flops:,}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento: {e}", exc_info=True)
            raise
    
    async def send_to_cloudflare(self, data):
        """
        Envia datos procesados a Cloudflare Worker vía aiohttp.
        """
        logger.info(f"📤 Enviando a Cloudflare Worker...")
        try:
            response = await self.pipeline.send_data(data)
            logger.info(f"✓ Respuesta recibida: {response.get('status')}")
            return response
        except Exception as e:
            logger.error(f"❌ Error al enviar: {e}", exc_info=True)
            raise
    
    async def run_pipeline(self):
        """
        Ejecuta el pipeline completo:
        1. Procesa matriz localmente
        2. Envia a Cloudflare Worker
        3. Recibe confirmación
        """
        logger.info("="*60)
        logger.info("🔮 AZAHEL NEMOTRIN - PIPELINE KPKAVE v2.0")
        logger.info("="*60)
        
        # Paso 1: Procesamiento local
        result = self.process_matrix()
        
        # Paso 2: Envío a Cloudflare
        cloudflare_response = await self.send_to_cloudflare(result)
        
        # Paso 3: Consolidar resultados
        final_output = {
            "local_processing": result,
            "cloudflare_response": cloudflare_response,
            "status": "success"
        }
        
        logger.info("="*60)
        logger.info("✓ PIPELINE COMPLETADO")
        logger.info(json.dumps(final_output, indent=2))
        logger.info("="*60)
        
        return final_output


async def main():
    """Punto de entrada del pipeline."""
    processor = AzaelProcessor(matrix_size=1000, batch_size=1000)
    await processor.run_pipeline()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️  Pipeline interrumpido por usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        sys.exit(1)
