#!/usr/bin/env python
"""
Script para generar INSERTs SQL desde los datos que me proporciones.
Pega los resultados de las consultas SQL aquí o en un archivo.
"""

from pathlib import Path
from datetime import datetime

def escape_sql_string(value):
    """Escapar string para SQL"""
    if value is None or value == '' or str(value).strip() == '':
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Escapar comillas simples y limpiar
        cleaned = str(value).replace("'", "''").replace('\n', ' ').replace('\r', ' ')
        return f"'{cleaned}'"
    # Convertir a string si es otro tipo
    cleaned = str(value).replace("'", "''").replace('\n', ' ').replace('\r', ' ')
    return f"'{cleaned}'"

def generate_inserts_from_data(table_name, columns, rows_data):
    """Generar INSERTs SQL desde datos"""
    if not rows_data:
        return []
    
    sql_lines = []
    sql_lines.append(f"\n-- Tabla: {table_name} ({len(rows_data)} registros)")
    
    for row in rows_data:
        # row puede ser una lista o diccionario
        if isinstance(row, dict):
            values = [escape_sql_string(row.get(col, '')) for col in columns]
        elif isinstance(row, (list, tuple)):
            values = [escape_sql_string(val) for val in row]
        else:
            continue
        
        columns_str = ', '.join(columns)
        values_str = ', '.join(values)
        sql_lines.append(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});")
    
    return sql_lines

def main():
    print("\n" + "=" * 70)
    print("  GENERAR INSERTS SQL DESDE DATOS")
    print("=" * 70 + "\n")
    
    print("Este script te ayudará a generar INSERTs SQL.")
    print("Puedes:")
    print("  1. Pegar los datos directamente aquí")
    print("  2. O crear un archivo con los datos")
    print("\nFormato esperado:")
    print("  tabla: nombre_tabla")
    print("  columnas: col1, col2, col3")
    print("  datos:")
    print("    valor1, valor2, valor3")
    print("    valor4, valor5, valor6")
    print()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"inserts_supabase_{timestamp}.sql"
    
    sql_content = []
    sql_content.append("-- ============================================")
    sql_content.append("-- Script SQL para insertar datos en Supabase")
    sql_content.append(f"-- Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_content.append("-- ============================================")
    sql_content.append("")
    sql_content.append("SET client_encoding TO 'UTF8';")
    sql_content.append("")
    
    print("Pega los datos aquí (o escribe 'archivo' para leer de un archivo):")
    print("(Escribe 'FIN' cuando termines)")
    print()
    
    current_table = None
    current_columns = None
    current_rows = []
    
    while True:
        try:
            line = input()
            if line.strip().upper() == 'FIN':
                break
            if line.strip().upper() == 'ARCHIVO':
                file_path = input("Ruta del archivo: ")
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                # Procesar líneas del archivo
                for file_line in lines:
                    # Procesar línea
                    pass
                continue
            
            # Detectar tabla
            if line.strip().startswith('===') and '===' in line:
                # Guardar tabla anterior si existe
                if current_table and current_columns and current_rows:
                    sql_content.extend(generate_inserts_from_data(current_table, current_columns, current_rows))
                    current_rows = []
                
                # Extraer nombre de tabla
                table_name = line.strip().replace('===', '').replace('AS tabla', '').strip()
                current_table = table_name
                current_columns = None
                print(f"[*] Procesando tabla: {current_table}")
            
            # Detectar columnas (primera fila de datos o header)
            elif current_table and not current_columns:
                # Intentar detectar columnas desde la primera fila de datos
                # O esperar que el usuario las especifique
                pass
            
            # Procesar filas de datos
            elif current_table and line.strip():
                # Asumir que es una fila de datos separada por comas o tabs
                values = [v.strip() for v in line.split('\t') if v.strip()]
                if values:
                    current_rows.append(values)
        
        except EOFError:
            break
        except KeyboardInterrupt:
            break
    
    # Guardar última tabla
    if current_table and current_columns and current_rows:
        sql_content.extend(generate_inserts_from_data(current_table, current_columns, current_rows))
    
    # Escribir archivo
    with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
        f.write('\n'.join(sql_content))
    
    print(f"\n[+] Archivo SQL generado: {output_file}")
    print(f"[*] Proximo paso: Ejecutar en Supabase SQL Editor")

if __name__ == '__main__':
    main()

