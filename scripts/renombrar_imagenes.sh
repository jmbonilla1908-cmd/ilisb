#!/bin/bash

# Script para renombrar las imágenes de los accesorios desde el proyecto antiguo
# al nuevo formato requerido por la aplicación Flask.

# --- INSTRUCCIONES ---
# 1. Asegúrate de que todas las imágenes originales (imageXX.jpg) estén en el directorio de destino.
# 2. Ejecuta este script desde el directorio raíz de tu proyecto: bash scripts/renombrar_imagenes.sh

echo "Iniciando el proceso de renombrado de imágenes de accesorios..."

# Directorio de destino donde están las imágenes
TARGET_DIR="app/static/img/accesorios"

# Directorio de origen (donde están las imágenes que ya copiaste)
SOURCE_DIR="app/static/img"

# 1. Crear el directorio de destino si no existe
mkdir -p "$TARGET_DIR"
echo "Directorio '$TARGET_DIR' asegurado."

# Mapa de nombres: "nombre_antiguo.ext" "nombre_nuevo.ext"
declare -A MAPA_NOMBRES=(
    ["image81.jpg"]="valv_compuerta.jpg"
    ["image24.jpg"]="valv_bola.jpg"
    ["image35.jpg"]="valv_globo.jpg"
    ["image44.jpg"]="valv_check_clapeta.jpg"
    ["image45.jpg"]="valv_check_bola.jpg"
    ["image32.jpg"]="valv_mariposa.jpg"
    ["image41.jpg"]="valv_pie.jpg"
    ["image83.jpg"]="codo_90_rl.jpg"
    ["image60.jpg"]="codo_90_rc.jpg"
    ["image61.jpg"]="codo_45.jpg"
    ["image82.jpg"]="curva_180.jpg"
    ["image58.jpg"]="tee_linea.jpg"
    ["image58a.jpg"]="tee_derivacion.jpg"
    # Para estos, usaremos imágenes genéricas o placeholders si no tienes una específica
    # Por ahora, el script los buscará. Si no los encuentra, lo advertirá.
    ["placeholder.jpg"]="entrada_normal.jpg"
    ["placeholder.jpg"]="salida_tuberia.jpg"
)

for antiguo in "${!MAPA_NOMBRES[@]}"; do
    nuevo=${MAPA_NOMBRES[$antiguo]}
    if [ -f "$SOURCE_DIR/$antiguo" ]; then
        echo "Moviendo y renombrando '$antiguo' a '$TARGET_DIR/$nuevo'..."
        mv "$SOURCE_DIR/$antiguo" "$TARGET_DIR/$nuevo"
    else
        echo "ADVERTENCIA: No se encontró el archivo de origen '$SOURCE_DIR/$antiguo'. Saltando."
    fi
done

echo "Proceso completado."