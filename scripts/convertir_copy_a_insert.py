#!/usr/bin/env python
"""
Script para convertir comandos COPY ... FROM stdin a INSERT statements
en el archivo SQL generado por pg_restore.
"""

import re
from pathlib import Path

def convertir_copy_a_insert(sql_file):
    """
    Convierte todos los comandos COPY ... FROM stdin a INSERT statements
    """
    sql_path = Path(sql_file)
    
    if not sql_path.exists():
        print(f"❌ Error: El archivo {sql_file} no existe")
        return False
    
    print("\n" + "=" * 70)
    print("  CONVERTIR COPY A INSERT")
    print("=" * 70 + "\n")
    print(f"[*] Archivo: {sql_file}\n")
    
    # Leer el archivo
    with open(sql_path, 'r', encoding='utf-8', errors='replace') as f:
        contenido = f.read()
    
    tamaño_original = len(contenido)
    print(f"[*] Tamaño original: {tamaño_original:,} bytes")
    
    # Crear backup
    backup_file = sql_path.with_suffix('.sql.backup3')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print(f"[*] Backup creado: {backup_file}\n")
    
    # Procesar línea por línea
    lineas = contenido.split('\n')
    lineas_nuevas = []
    en_copy = False
    tabla_actual = None
    columnas = []
    datos_copy = []
    
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        
        # Detectar inicio de COPY
        if 'COPY public.' in linea and 'FROM stdin;' in linea:
            en_copy = True
            # Extraer tabla y columnas
            match = re.search(r'COPY public\.(\w+)\s*\(([^)]+)\)\s*FROM stdin;', linea)
            if match:
                tabla_actual = match.group(1)
                columnas = [col.strip() for col in match.group(2).split(',')]
                print(f"   [*] Convirtiendo COPY para tabla: {tabla_actual} ({len(columnas)} columnas)")
                datos_copy = []
            else:
                # Sin columnas especificadas, necesitamos obtenerlas de otra manera
                match = re.search(r'COPY public\.(\w+)\s*FROM stdin;', linea)
                if match:
                    tabla_actual = match.group(1)
                    columnas = []
                    print(f"   [*] Convirtiendo COPY para tabla: {tabla_actual} (sin columnas especificadas)")
                    datos_copy = []
            i += 1
            continue
        
        # Si estamos en modo COPY, recopilar datos
        if en_copy:
            # Detectar fin de COPY
            if linea.strip() == '\\.':
                # Convertir datos a INSERT statements
                if datos_copy and tabla_actual:
                    print(f"      [+] {len(datos_copy)} registros encontrados")
                    for datos in datos_copy:
                        if datos.strip():
                            # Dividir por tabulaciones, pero preservar espacios dentro de valores
                            valores = datos.split('\t')
                            # Limpiar y escapar valores
                            valores_limpios = []
                            for j, valor in enumerate(valores):
                                valor_original = valor
                                valor = valor.strip()
                                
                                # Manejar NULL
                                if valor == '' or valor == '\\N' or valor.lower() == 'null':
                                    valores_limpios.append('NULL')
                                # Verificar si es booleano PRIMERO (antes de escapar comillas)
                                elif valor.lower() in ('t', 'f', 'true', 'false'):
                                    if valor.lower() in ('t', 'true'):
                                        valores_limpios.append('TRUE')
                                    else:
                                        valores_limpios.append('FALSE')
                                else:
                                    # Escapar comillas simples
                                    valor = valor.replace("'", "''")
                                    # Intentar determinar el tipo
                                    es_numerico = False
                                    # Verificar si es entero
                                    try:
                                        int(valor)
                                        valores_limpios.append(valor)
                                        es_numerico = True
                                    except ValueError:
                                        # Verificar si es decimal
                                        try:
                                            float(valor)
                                            valores_limpios.append(valor)
                                            es_numerico = True
                                        except ValueError:
                                            # Es texto, poner comillas
                                            valores_limpios.append(f"'{valor}'")
                            
                            # Generar INSERT
                            if columnas:
                                columnas_str = ', '.join(columnas)
                                valores_str = ', '.join(valores_limpios)
                                lineas_nuevas.append(f"INSERT INTO public.{tabla_actual} ({columnas_str}) VALUES ({valores_str});")
                            else:
                                valores_str = ', '.join(valores_limpios)
                                lineas_nuevas.append(f"INSERT INTO public.{tabla_actual} VALUES ({valores_str});")
                
                en_copy = False
                tabla_actual = None
                columnas = []
                datos_copy = []
                i += 1
                continue
            
            # Recopilar datos (hasta encontrar \.)
            if linea.strip() and not linea.strip().startswith('--'):
                datos_copy.append(linea)
            
            i += 1
            continue
        
        # Línea normal, agregar tal cual
        lineas_nuevas.append(linea)
        i += 1
    
    # Escribir archivo convertido
    contenido_nuevo = '\n'.join(lineas_nuevas)
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write(contenido_nuevo)
    
    tamaño_nuevo = len(contenido_nuevo)
    print(f"\n[+] Archivo SQL convertido guardado: {sql_file}")
    print(f"[+] Tamaño original: {tamaño_original:,} bytes")
    print(f"[+] Tamaño nuevo: {tamaño_nuevo:,} bytes")
    print(f"[+] Diferencia: {tamaño_nuevo - tamaño_original:,} bytes")
    
    return True

def main():
    sql_file = r"C:\Users\User\Downloads\BASEDEHORAIO_PARA_SUPABASE.sql"
    
    if convertir_copy_a_insert(sql_file):
        print("\n" + "=" * 70)
        print("  CONVERSIÓN COMPLETADA")
        print("=" * 70)
        print(f"\n✅ Archivo SQL convertido: {sql_file}")
        print("\n📝 Todos los comandos COPY han sido convertidos a INSERT statements")
        print("   Ahora puedes ejecutar este archivo en Supabase SQL Editor")
    else:
        print("\n❌ La conversión falló.")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

