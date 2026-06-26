#!/bin/bash

# Azahel Nemotrin - Setup Script
# Setup rápido para Termux

set -e

echo "================================================"
echo "  AZAHEL NEMOTRIN - Setup KPKAVE v2.0"
echo "================================================"
echo ""

# Detectar si está en Termux
if [ ! -d "$HOME/storage" ]; then
    echo "⚠️  Este script está optimizado para Termux."
    echo "   En otros sistemas, instala manualmente desde requirements.txt"
fi

# Paso 1: Actualizar paquetes
echo "[1/5] Actualizando paquetes del sistema..."
pkg update -y
pkg upgrade -y

# Paso 2: Instalar Python y pip
echo "[2/5] Instalando Python 3.11..."
pkg install python -y
python --version

# Paso 3: Crear directorio de modelos
echo "[3/5] Creando estructura de directorios..."
mkdir -p ~/storage/shared/Azael_KpKave/modelos
mkdir -p ./logs
mkdir -p ./data

# Paso 4: Instalar dependencias Python
echo "[4/5] Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Paso 5: Configurar variables de entorno
echo "[5/5] Configurando .env..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env creado desde .env.example"
    echo "⚠️  Edita .env con tus credenciales de Cloudflare y Nvidia"
else
    echo "✓ .env ya existe"
fi

echo ""
echo "================================================"
echo "✓ SETUP COMPLETADO"
echo "================================================"
echo ""
echo "Próximos pasos:"
echo "  1. Edita .env con tus credenciales"
echo "  2. Corre: python src/pytorch_processor.py"
echo "  3. Deploy Worker: wrangler deploy"
echo ""
echo "Documentación: Ver README.md"
echo ""
