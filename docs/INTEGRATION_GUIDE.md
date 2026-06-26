# AZAHEL NEMOTRON - GUÍA DE INTEGRACIÓN KPKAVE v2.5

## 📋 Descripción General

Este documento describe cómo integrar completamente el pipeline End-to-End:

```
[Termux - Celular]
    PyTorch Processor (1.14 GFLOPS)
         ↓ (KPKAVE Contract)
[Cloudflare Workers]
    BÚNKER DE BORDE v2.5
         ↓ (Validated + Transaction ID)
[Edge Storage]
    KV Store / Analytics
```

---

## 🔧 Configuración Rápida (5 minutos)

### 1. Clonar y Setup
```bash
git clone https://github.com/velazquezcampos96-coder/Azahel-nemotrin
cd Azahel-nemotrin

# Setup automático (Termux)
bash scripts/setup.sh
```

### 2. Crear `.env` con tus credenciales
```bash
cp .env.example .env
nano .env
```

**IMPORTANTE:** Edita `CLOUDFLARE_WORKER_URL` con tu URL real:
```dotenv
CLOUDFLARE_WORKER_URL=https://procesos.tu-dominio.com/api/v1/process
```

### 3. Deploy Cloudflare Worker
```bash
# Instala wrangler (si no lo tienes)
npm install -g wrangler

# O usa la web UI de Cloudflare Dashboard
# Copia el contenido de workers/azahel-nemotron-edge-bunker.js
# En Dashboard → Workers → Nueva función
```

### 4. Test rápido
```bash
python scripts/test-connection.py
```

Deberías ver:
```
[2026-06-26 10:15:32] [INFO] ✓ Conexión exitosa
[2026-06-26 10:15:32] [INFO] Response: {...}
```

### 5. Ejecutar Pipeline
```bash
python src/pytorch_processor.py
```

---

## 📊 Contrato de Datos KPKAVE v2.5

### Input (Termux → Cloudflare)
```json
{
  "gflops": 1.14,
  "tiempo_procesamiento": 47.1643,
  "dispositivo": "Termux-Linux-armv8l",
  "matrix_size": 1000,
  "total_flops": 2000000000,
  "timestamp_local": "2026-06-26T10:15:32.123456"
}
```

**Campos Requeridos (KPKAVE):**
- `gflops` (float): Gigaflops procesados
- `tiempo_procesamiento` (float): Segundos de ejecución
- `dispositivo` (string): Identificación del device

### Output (Cloudflare → Termux)
```json
{
  "mensaje": "PIPELINE COMPLETADO EN EL BORDE",
  "validado": true,
  "meta": {
    "transactionId": "TXN-1719379782450-ABC9XYZ-0042",
    "status": "SUCCESS",
    "gflops": 1.14,
    "tiempo": 47.1643,
    "nodo": "Termux-Linux-armv8l",
    "fecha": "2026-06-26T10:15:32.123456Z",
    "payloadHash": "3f4a8c9d...",
    "cloudflare": {
      "version": "v2.5",
      "pais": "MX",
      "colo": "MEX"
    }
  }
}
```

---

## 🔒 Seguridad

### Variables de Entorno
- **Nunca** commites `.env` con keys reales
- Usa `.gitignore` para proteger `.env`
- Guarda keys en variables de entorno del sistema

```bash
# En Termux, guardarlo de forma segura:
echo 'export CLOUDFLARE_WORKER_URL="tu-url-real"' >> ~/.bashrc
source ~/.bashrc
```

### Validación de Payload
Cada request incluye:
- **Firma SHA256** del payload (integridad)
- **X-Signature header** para verificación
- **Request ID único** para auditoría

---

## 🐛 Debugging

### Ver logs detallados
```bash
# En .env:
LOG_LEVEL=DEBUG

# Ejecutar:
python src/pytorch_processor.py 2>&1 | tee logs/debug.log
```

### Test de conexión
```bash
python src/async_client.py  # Test directo del cliente
python scripts/test-connection.py  # Test completo
```

### Ver KV Store (si tienes acceso)
```bash
# En Cloudflare Dashboard
# Workers → KV → Verifica RENDIMIENTO_KV
```

---

## 📈 Performance Esperado

| Métrica | Valor |
|---------|-------|
| **Latencia Celular→Worker** | <100ms (con internet) |
| **Procesamiento PyTorch** | ~47s (matriz 1000x1000) |
| **Validación Edge** | <5ms |
| **Total Pipeline** | ~47-48s |
| **Costo Mensual** | $0 (gratis) |

---

## 🚀 Siguiente Paso: Entrenar Nemotron (Opcional)

Si quieres un LLM que hable como Azahel:

1. Usa el notebook de Colab (`scripts/colab_finetune.ipynb`)
2. Fine-tune Nemotron-Mini-4B con datos de Enoc/Salomón
3. Deploy el modelo en Hugging Face
4. Integra en el Worker para respuestas inteligentes

---

## 📞 Troubleshooting

### Error: "CLOUDFLARE_WORKER_URL no configurada"
```bash
nano .env
# Edita CLOUDFLARE_WORKER_URL con tu URL real
```

### Error: "Timeout de conexión"
```bash
# Aumenta timeout en .env:
PROCESS_TIMEOUT=120
RETRY_ATTEMPTS=5
```

### Error: "Worker respond con 400"
```bash
# El payload no cumple KPKAVE v2.5
# Verifica que tenga: gflops, tiempo_procesamiento, dispositivo
```

### Error: "Falló después de 3 intentos"
```bash
# Posibles causas:
# 1. Sin internet (verifica conexión)
# 2. Worker no deployado (verifica Dashboard)
# 3. URL incorrecta (verifica .env)
```

---

## 🎯 Arquitectura Final

```
┌─────────────────────────────────┐
│   TERMUX (Celular - Neza)      │
│  ┌──────────────────────────┐   │
│  │ pytorch_processor.py     │   │
│  │ • Matriz 1000x1000       │   │
│  │ • Calcula 1.14 GFLOPS    │   │
│  │ • Empaqueta KPKAVE v2.5  │   │
│  └────────────┬─────────────┘   │
└───────────────┼──────────────────┘
                │ HTTPS POST
┌───────────────▼──────────────────┐
│  CLOUDFLARE WORKERS (Edge)       │
│  ┌──────────────────────────┐    │
│  │ azahel-nemotron-edge-    │    │
│  │ bunker.js (v2.5)         │    │
│  │ • Valida payload         │    │
│  │ • Genera TX-ID único     │    │
│  │ • Calcula hash SHA256    │    │
│  │ • Almacena en KV Store   │    │
│  └────────────┬─────────────┘    │
└───────────────┼──────────────────┘
                │ JSON Response
┌───────────────▼──────────────────┐
│   TERMUX (Resultado Final)       │
│   • Transaction ID: TXN-xxx      │
│   • Status: SUCCESS              │
│   • Hash: 3f4a8c9d...            │
└─────────────────────────────────┘
```

---

**Pipeline KPKAVE v2.5 Completo. Vigilante #201 activado. 🔥**
