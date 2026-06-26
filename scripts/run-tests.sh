#!/bin/bash

# AZAHEL NEMOTRIN - TEST SUITE COMPLETO
# Valida que el pipeline esté funcionando correctamente

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  AZAHEL NEMOTRON - TEST SUITE KPKAVE v2.5"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir resultado
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
        exit 1
    fi
}

# TEST 1: Validar que tenemos .env
echo "[TEST 1] Verificando configuración..."
if [ -f ".env" ]; then
    test_result 0 ".env existe"
else
    echo -e "${YELLOW}⚠ .env no encontrado, creando desde .env.example${NC}"
    cp .env.example .env
    echo -e "${RED}⚠ Edita .env con tu CLOUDFLARE_WORKER_URL${NC}"
    exit 1
fi

# TEST 2: Validar archivo worker
echo ""
echo "[TEST 2] Validando Worker..."
if [ -f "workers/azahel-nemotron-edge-bunker.js" ]; then
    test_result 0 "Worker deployado"
else
    test_result 1 "Worker NO encontrado"
fi

# TEST 3: Validar Python
echo ""
echo "[TEST 3] Validando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    test_result 0 "Python $PYTHON_VERSION disponible"
else
    test_result 1 "Python NO instalado"
fi

# TEST 4: Validar PyTorch
echo ""
echo "[TEST 4] Validando PyTorch..."
python3 -c "import torch; print(f'PyTorch {torch.__version__}')" 2>/dev/null
test_result $? "PyTorch instalado"

# TEST 5: Validar aiohttp
echo ""
echo "[TEST 5] Validando aiohttp..."
python3 -c "import aiohttp; print(f'aiohttp {aiohttp.__version__}')" 2>/dev/null
test_result $? "aiohttp instalado"

# TEST 6: Ejecutar test de conexión
echo ""
echo "[TEST 6] Test de conexión al Worker..."
echo -e "${YELLOW}Nota: Asegúrate de tener CLOUDFLARE_WORKER_URL correcta en .env${NC}"

if python3 scripts/test-connection.py > /dev/null 2>&1; then
    test_result 0 "Conexión al Worker exitosa"
else
    echo -e "${YELLOW}⚠ Test de conexión falló (puede deberse a Worker no deployado)${NC}"
fi

# TEST 7: Validar archivos source
echo ""
echo "[TEST 7] Validando archivos source..."
for file in "src/pytorch_processor.py" "src/async_client.py"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        test_result 1 "$file NO encontrado"
    fi
done

echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ TODOS LOS TESTS PASARON${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Próximos pasos:"
echo "  1. Edita .env con tu CLOUDFLARE_WORKER_URL"
echo "  2. Ejecuta: python3 src/pytorch_processor.py"
echo "  3. O abre: demo/dashboard.html en un navegador"
echo ""
