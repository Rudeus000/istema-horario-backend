#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir problemas de codificación en el archivo .env
"""
import os
import sys
from pathlib import Path

def corregir_env():
    """Corrige problemas de codificación en el archivo .env"""
    
    # Obtener la ruta del archivo .env
    project_root = Path(__file__).parent.parent
    env_path = project_root / '.env'
    
    if not env_path.exists():
        print("❌ El archivo .env no existe!")
        print(f"   Ruta esperada: {env_path}")
        return False
    
    print(f"📖 Leyendo archivo: {env_path}")
    
    # Intentar leer con diferentes codificaciones
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    content = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            with open(env_path, 'r', encoding=encoding) as f:
                content = f.read()
            used_encoding = encoding
            print(f"✅ Archivo leído correctamente con codificación: {encoding}")
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        print("❌ No se pudo leer el archivo con ninguna codificación conocida")
        return False
    
    # Limpiar el contenido
    lines = content.splitlines()
    cleaned_lines = []
    
    for line in lines:
        # Eliminar caracteres de control invisibles excepto saltos de línea
        cleaned_line = ''.join(char for char in line if ord(char) >= 32 or char in '\t')
        cleaned_lines.append(cleaned_line)
    
    # Reconstruir el contenido
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Si el contenido cambió, guardarlo en UTF-8
    if cleaned_content != content:
        print("🔧 Limpiando caracteres problemáticos...")
    
    # Crear backup
    backup_path = env_path.with_suffix('.env.backup')
    try:
        with open(env_path, 'rb') as src:
            with open(backup_path, 'wb') as dst:
                dst.write(src.read())
        print(f"💾 Backup creado: {backup_path}")
    except Exception as e:
        print(f"⚠️  No se pudo crear backup: {e}")
    
    # Guardar en UTF-8 sin BOM
    try:
        with open(env_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cleaned_content)
        print("✅ Archivo .env guardado correctamente en UTF-8")
        print("")
        print("💡 Si el problema persiste, verifica que:")
        print("   1. La contraseña no tenga caracteres especiales problemáticos")
        print("   2. El archivo .env esté guardado sin BOM (Byte Order Mark)")
        print("   3. Todas las líneas terminen correctamente")
        return True
    except Exception as e:
        print(f"❌ Error al guardar el archivo: {e}")
        return False

if __name__ == '__main__':
    success = corregir_env()
    sys.exit(0 if success else 1)

