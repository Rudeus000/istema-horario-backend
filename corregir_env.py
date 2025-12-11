#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Corregir archivo .env directamente"""
from pathlib import Path

env_path = Path('.env')

# Intentar leer con diferentes codificaciones
encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
content = None
used_encoding = None

for encoding in encodings:
    try:
        with open(env_path, 'r', encoding=encoding) as f:
            content = f.read()
        used_encoding = encoding
        print(f"✅ Leído con codificación: {encoding}")
        break
    except Exception as e:
        continue

if not content:
    print("❌ No se pudo leer el archivo")
    exit(1)

# Limpiar contenido
lines = content.splitlines()
cleaned_lines = []
for line in lines:
    # Eliminar caracteres de control problemáticos
    cleaned = ''.join(c if ord(c) >= 32 or c in '\t' else '' for c in line)
    cleaned_lines.append(cleaned)

cleaned_content = '\n'.join(cleaned_lines)

# Crear backup
backup_path = env_path.with_suffix('.env.backup')
with open(env_path, 'rb') as src:
    with open(backup_path, 'wb') as dst:
        dst.write(src.read())
print(f"💾 Backup: {backup_path}")

# Guardar en UTF-8 sin BOM
with open(env_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(cleaned_content)
print("✅ Archivo .env corregido y guardado en UTF-8")

