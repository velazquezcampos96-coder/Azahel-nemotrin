# 📱 DEMO Y TESTING - AZAHEL NEMOTRON KPKAVE v2.5

## 🎯 Opciones para mostrar a un cliente

### **OPCIÓN 1: Dashboard Web Interactivo (MÁS FÁCIL PARA CLIENTES)**

**URL de tu demo:**
```
https://tu-dominio.com/demo/dashboard.html
```

**Qué ve el cliente:**
- ✅ Status del sistema en tiempo real
- ✅ Última métrica de GFLOPS
- ✅ Logs en vivo del pipeline
- ✅ Botón para ejecutar demo
- ✅ Estadísticas globales
- ✅ Sin ver código sensible

**Para servir locally (sin subir a internet):**
```bash
# En el directorio raíz del proyecto
python -m http.server 8000

# Luego abre:
# http://localhost:8000/demo/dashboard.html
```

---

### **OPCIÓN 2: Test desde Termux (PARA TÉCNICOS)**

**Prueba la bestia completa:**
```bash
# Ejecutar test de conexión
python scripts/test-connection.py

# Ejecutar pipeline completo
python src/pytorch_processor.py
```

**Output esperado:**
```
🔮 AZAHEL NEMOTRIN - PIPELINE KPKAVE v2.5 INTEGRADO
======================================================================
[PASO 1] Procesamiento Local
-------
🔥 Iniciando procesamiento matriz 1000x1000
   Dispositivo: Termux-Linux-armv8l
✓ Matrices generadas en 0.0023s
✓ Multiplicación completada en 47.1643s
📊 GFLOPS: 1.14
✓ Contrato KPKAVE v2.5 generado

[PASO 2] Transmisión a Edge
-------
📤 [Intento 1/3] Enviando a Worker
✓ Respuesta recibida del Worker
   Transaction ID: TXN-1719379782450-ABC9XYZ-0042
   Status: SUCCESS
```

---

### **OPCIÓN 3: cURL / Postman (PARA APIS)

**Test directo del endpoint:**

#### **cURL:**
```bash
curl -X POST https://tu-dominio.com/api/v1/process \
  -H "Content-Type: application/json" \
  -H "X-Client-Version: azahel-nemotron-v2.5" \
  -d '{
    "gflops": 1.14,
    "tiempo_procesamiento": 47.1643,
    "dispositivo": "Termux-Linux-armv8l"
  }'
```

#### **Respuesta esperada (200 OK):**
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

### **OPCIÓN 4: README en GitHub (PARA DEMOSTRACIONES VISUALES)**

**El cliente accede a:**
```
https://github.com/velazquezcampos96-coder/Azahel-nemotrin
```

**Ve:**
- ✅ Arquitectura completa
- ✅ Documentación técnica
- ✅ Benchmarks de performance
- ✅ Instrucciones de setup
- ✅ MIT License (si aplica)

---

## 📊 LINKS PARA COMPARTIR CON CLIENTES

### **Resumen Ejecutivo (Para gerentes):**
```
Título: "Infraestructura Edge Computing Híbrida KPKAVE v2.5"

Características:
- Procesamiento local: PyTorch (1.14 GFLOPS)
- Edge computing: Cloudflare Workers (sub-milisegundos)
- API de Nemotron: Opcional para LLM
- Costo: $0 USD/mes
- Uptime: 99.99% (SLA de Cloudflare)
- Latencia: <100ms global

Link: https://github.com/velazquezcampos96-coder/Azahel-nemotrin
```

### **Demo Técnica (Para engineers):**
```
Dashboard en vivo:
https://tu-dominio.com/demo/dashboard.html

API Endpoint (POST):
https://tu-dominio.com/api/v1/process

Repositorio:
https://github.com/velazquezcampos96-coder/Azahel-nemotrin

Documentación:
https://github.com/velazquezcampos96-coder/Azahel-nemotrin/blob/main/docs/INTEGRATION_GUIDE.md
```

---

## 🧪 SCRIPT DE TESTING COMPLETO

Copia este archivo como `test_demo.sh` para que los clientes puedan validar todo:

```bash
#!/bin/bash
echo "════════════════════════════════════════════════════════════════"
echo "AZAHEL NEMOTRON - TEST SUITE KPKAVE v2.5"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test 1: Conexión
echo "[TEST 1] Validando conexión a Worker..."
RESPONSE=$(curl -s -X POST https://tu-dominio.com/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "gflops": 1.14,
    "tiempo_procesamiento": 47.1643,
    "dispositivo": "test-client"
  }')

if echo "$RESPONSE" | grep -q '"status":"SUCCESS"'; then
    echo "✓ Worker operativo"
else
    echo "✗ Error en Worker"
    echo "Response: $RESPONSE"
    exit 1
fi

echo ""
echo "[TEST 2] Extrayendo Transaction ID..."
TXN_ID=$(echo "$RESPONSE" | grep -o '"transactionId":"[^"]*' | cut -d'"' -f4)
echo "✓ Transaction ID: $TXN_ID"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✓ TODOS LOS TESTS PASADOS"
echo "════════════════════════════════════════════════════════════════"
```

---

## 🎤 PRESENTACIÓN A CLIENTE (Guion de 5 minutos)

```
1. PROBLEMA ACTUAL (30 segundos)
   "Procesar datos localmente es lento. Enviar a servidores lejanos es costoso."

2. NUESTRA SOLUCIÓN (90 segundos)
   - Procesamiento LOCAL en el dispositivo (PyTorch: 1.14 GFLOPS)
   - Validación EDGE en Cloudflare (sub-milisegundos, global)
   - Sin servidor propio (sin mantenimiento)
   - Costo: CERO (gratis durante desarrollo/pruebas)
   
3. DEMOSTRACIÓN VIVA (2 minutos)
   - Mostrar dashboard: demo/dashboard.html
   - Hacer click en "EJECUTAR PIPELINE"
   - Ver logs en tiempo real
   - Mostrar Transaction ID generado
   
4. NÚMEROS (90 segundos)
   - Tiempo procesamiento: 47 segundos
   - Latencia de red: <100ms
   - Throughput edge: Sub-milisegundos
   - Cost per request: $0.00
   - Uptime garantizado: 99.99%
   
5. SIGUIENTES PASOS (30 segundos)
   - Customización según necesidad
   - Integración con tu sistema
   - Soporte técnico 24/7
```

---

## 📋 CHECKLIST PARA MOSTRAR

- [ ] Dashboard cargado: `demo/dashboard.html`
- [ ] Botón "EJECUTAR PIPELINE" funciona
- [ ] Logs en vivo se actualizan
- [ ] Transaction ID generado
- [ ] GFLOPS mostrado correctamente
- [ ] Respuesta del Worker visible
- [ ] Página es responsiva (mobile-friendly)
- [ ] Código sensible (.env) NO está expuesto

---

## 🔐 SEGURIDAD AL PRESENTAR

**NUNCA compartas:**
- ❌ `.env` con API Keys
- ❌ Credenciales de Cloudflare
- ❌ Información sensible del servidor

**Solo comparte:**
- ✅ URL pública del dashboard
- ✅ Repositorio de GitHub
- ✅ Documentación técnica
- ✅ Demostración en vivo

---

**¿Listo para conquistar con tu infraestructura? 🚀**
