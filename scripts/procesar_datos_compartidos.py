#!/usr/bin/env python
"""
Script para procesar los datos compartidos desde PostgreSQL y generar SQL INSERTs completos.
Maneja problemas de encoding y genera el script SQL final.
"""

import re
from pathlib import Path
from datetime import datetime

def clean_encoding(text):
    """Limpiar problemas de encoding comunes"""
    if not text:
        return text
    text = str(text)
    # Mapeo de caracteres mal codificados
    replacements = {
        '├í': 'á', '├®': 'é', '├¡': 'í', '├│': 'ó', '├║': 'ú',
        '├ü': 'Á', '├ë': 'É', '├ì': 'Í', '├ô': 'Ó', '├Ü': 'Ú',
        '├▒': 'ñ', '├æ': 'Ñ', '├»': 'ü', '├╝': 'Ü',
        '├ë': 'É', '├ì': 'Í', '├ô': 'Ó', '├Ü': 'Ú',
        '├Ç': 'Ç', '├º': 'ç',
        '├║': 'ú', '├║': 'ú',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def escape_sql(value):
    """Escapar valor para SQL"""
    if value is None or value == '' or str(value).strip() == '':
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float)):
        return str(value)
    # Limpiar encoding y escapar
    cleaned = clean_encoding(str(value))
    cleaned = cleaned.replace("'", "''").replace('\n', ' ').replace('\r', ' ')
    return f"'{cleaned}'"

def generate_inserts_from_data(table_name, columns, rows_data):
    """Generar INSERT statements desde datos"""
    if not rows_data:
        return []
    
    sql_lines = []
    sql_lines.append(f"\n-- ============================================")
    sql_lines.append(f"-- {table_name} ({len(rows_data)} registros)")
    sql_lines.append(f"-- ============================================")
    sql_lines.append("")
    
    for row in rows_data:
        values = [escape_sql(row.get(col)) for col in columns]
        values_str = ', '.join(values)
        sql_lines.append(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({values_str});")
    
    return sql_lines

def main():
    print("\n" + "=" * 70)
    print("  PROCESAR DATOS COMPARTIDOS Y GENERAR SQL")
    print("=" * 70 + "\n")
    
    # Este script será usado para procesar los datos que el usuario compartió
    # Por ahora, genero la estructura base
    
    output_file = Path(__file__).parent / "inserts_supabase_FINAL_COMPLETO.sql"
    
    sql = []
    sql.append("-- ============================================")
    sql.append("-- Script SQL COMPLETO para insertar datos en Supabase")
    sql.append(f"-- Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql.append("-- ============================================")
    sql.append("")
    sql.append("SET client_encoding TO 'UTF8';")
    sql.append("")
    sql.append("-- IMPORTANTE: Ejecutar este script en Supabase SQL Editor")
    sql.append("-- después de haber ejecutado create_supabase_database.sql")
    sql.append("")
    
    # Nota: Los datos completos se agregarán manualmente o mediante procesamiento
    # de los datos compartidos por el usuario
    
    sql.append("-- ============================================")
    sql.append("-- NOTA: Este archivo se completará con los datos proporcionados")
    sql.append("-- ============================================")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql))
    
    print(f"[+] Archivo base creado: {output_file}")
    print(f"\n[*] Procesando datos compartidos...")
    print(f"[*] Los INSERTs completos se generarán en el siguiente paso.")

if __name__ == '__main__':
    main()

