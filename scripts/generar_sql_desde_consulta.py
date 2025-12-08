#!/usr/bin/env python
"""
Script para generar INSERTs SQL desde los datos de las consultas PostgreSQL.
Limpia caracteres problemáticos de encoding.
"""

from pathlib import Path
from datetime import datetime

def clean_text(text):
    """Limpiar texto de caracteres problemáticos"""
    if text is None:
        return None
    # Mapeo de caracteres problemáticos comunes
    replacements = {
        '├í': 'á', '├®': 'é', '├¡': 'í', '├│': 'ó', '├║': 'ú',
        '├ü': 'Á', '├ë': 'É', '├ì': 'Í', '├ô': 'Ó', '├Ü': 'Ú',
        '├▒': 'ñ', '├æ': 'Ñ', '├»': 'ü', '├╝': 'Ü',
        '├ë': 'É', '├ì': 'Í', '├ô': 'Ó', '├Ü': 'Ú',
        '├Ç': 'Ç', '├º': 'ç',
    }
    text = str(text)
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def escape_sql(value):
    """Escapar valor para SQL"""
    if value is None or value == '':
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float)):
        return str(value)
    # Limpiar y escapar string
    cleaned = clean_text(value)
    cleaned = cleaned.replace("'", "''").replace('\n', ' ').replace('\r', ' ')
    return f"'{cleaned}'"

def main():
    print("\n" + "=" * 70)
    print("  GENERAR SQL DESDE DATOS DE CONSULTA")
    print("=" * 70 + "\n")
    
    print("Este script generará el SQL completo.")
    print("Por favor, pega los datos que faltan o ejecuta las consultas faltantes.\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"inserts_supabase_{timestamp}.sql"
    
    sql = []
    sql.append("-- ============================================")
    sql.append("-- Script SQL para insertar datos en Supabase")
    sql.append(f"-- Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql.append("-- ============================================")
    sql.append("")
    sql.append("SET client_encoding TO 'UTF8';")
    sql.append("")
    
    # Aquí puedes agregar manualmente los INSERTs o usar los datos que ya tienes
    # Por ahora, genero la estructura base
    
    print(f"[*] Archivo base creado: {output_file}")
    print(f"\n[*] Para completar, necesitas proporcionar:")
    print(f"    1. academic_setup_tipounidadacademica")
    print(f"    2. academic_setup_seccion")
    print(f"    3. academic_setup_espaciosfisicos")
    print(f"    4. users_roles")
    print(f"    5. academic_setup_carreramaterias")
    print(f"    6. users_docenteespecialidades")
    print(f"    7. scheduling_grupos")
    print(f"    8. scheduling_disponibilidaddocentes")
    print(f"\n[*] O ejecuta estas consultas en PostgreSQL:")
    print(f"    SELECT * FROM academic_setup_tipounidadacademica;")
    print(f"    SELECT * FROM academic_setup_seccion;")
    print(f"    -- etc...")
    
    with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
        f.write('\n'.join(sql))
    
    print(f"\n[+] Archivo creado: {output_file}")

if __name__ == '__main__':
    main()

