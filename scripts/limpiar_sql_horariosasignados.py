#!/usr/bin/env python
"""
Script para eliminar completamente la tabla scheduling_horariosasignados
del archivo SQL generado por pg_restore.
"""

import re
from pathlib import Path

def limpiar_tabla_del_sql(sql_file, tabla_excluir='scheduling_horariosasignados'):
    """
    Elimina completamente una tabla del archivo SQL
    """
    sql_path = Path(sql_file)
    
    if not sql_path.exists():
        print(f"❌ Error: El archivo {sql_file} no existe")
        return False
    
    print("\n" + "=" * 70)
    print("  LIMPIAR TABLA DEL ARCHIVO SQL")
    print("=" * 70 + "\n")
    print(f"[*] Archivo: {sql_file}")
    print(f"[*] Tabla a excluir: {tabla_excluir}\n")
    
    # Leer el archivo
    with open(sql_path, 'r', encoding='utf-8', errors='replace') as f:
        contenido = f.read()
    
    tamaño_original = len(contenido)
    print(f"[*] Tamaño original: {tamaño_original:,} bytes")
    
    # Crear backup
    backup_file = sql_path.with_suffix('.sql.backup2')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print(f"[*] Backup creado: {backup_file}\n")
    
    # Patrones para eliminar (usando regex)
    patrones = [
        # Comentarios TOC relacionados con la tabla
        (rf'--.*?Name: {tabla_excluir}.*?\n(?:--.*?\n)*', ''),
        # Definición de tabla (desde comentarios hasta el cierre)
        (rf'--.*?{tabla_excluir}.*?\n(?:--.*?\n)*.*?\);', ''),
        # Comandos COPY
        (rf'COPY public\.{tabla_excluir}.*?\\\.\n', ''),
        # Comandos ALTER TABLE
        (rf'ALTER TABLE.*?{tabla_excluir}.*?\n', ''),
        # CREATE INDEX
        (rf'CREATE INDEX.*?{tabla_excluir}.*?\n', ''),
        # CREATE SEQUENCE
        (rf'CREATE SEQUENCE.*?{tabla_excluir}.*?\n', ''),
        # SEQUENCE SET
        (rf'--.*?SEQUENCE SET.*?{tabla_excluir}.*?\n.*?SELECT.*?setval.*?{tabla_excluir}.*?\n', ''),
        # Constraints
        (rf'--.*?CONSTRAINT.*?{tabla_excluir}.*?\n.*?ALTER TABLE.*?{tabla_excluir}.*?\n.*?ADD CONSTRAINT.*?\n', ''),
    ]
    
    # Método más simple: eliminar líneas que contengan la tabla
    lineas = contenido.split('\n')
    lineas_filtradas = []
    excluir_bloque = False
    excluir_copy = False
    nivel_parentesis = 0
    
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        
        # Detectar inicio de bloque de tabla
        if tabla_excluir in linea:
            # Verificar si es un comentario TOC
            if '--' in linea and ('TOC entry' in linea or 'Name:' in linea):
                excluir_bloque = True
                print(f"   [-] Eliminando bloque de tabla (línea {i+1})")
                # Saltar hasta el siguiente bloque importante
                while i < len(lineas) - 1:
                    i += 1
                    siguiente = lineas[i]
                    # Detectar fin: nuevo TOC entry que no es de esta tabla
                    if '--' in siguiente and 'TOC entry' in siguiente and tabla_excluir not in siguiente:
                        break
                    # Detectar fin: CREATE TABLE de otra tabla
                    if siguiente.strip().startswith('CREATE TABLE') and tabla_excluir not in siguiente:
                        break
                continue
            
            # Detectar COPY
            if 'COPY public.' + tabla_excluir in linea:
                excluir_copy = True
                print(f"   [-] Eliminando datos COPY (línea {i+1})")
                while i < len(lineas) - 1:
                    i += 1
                    if lineas[i].strip() == '\\.':
                        excluir_copy = False
                        break
                continue
            
            # Detectar otros comandos relacionados
            if any(cmd in linea for cmd in [
                'CREATE TABLE', 'ALTER TABLE', 'CREATE INDEX', 
                'CREATE SEQUENCE', 'SEQUENCE SET', 'setval', 'CONSTRAINT'
            ]):
                print(f"   [-] Eliminando comando relacionado (línea {i+1})")
                # Si es ALTER TABLE o CREATE, puede tener múltiples líneas
                if 'ALTER TABLE' in linea or 'CREATE' in linea:
                    while i < len(lineas) - 1:
                        i += 1
                        siguiente = lineas[i]
                        if siguiente.strip().endswith(';') or siguiente.strip() == '':
                            break
                continue
        
        # Si estamos en modo COPY, seguir excluyendo
        if excluir_copy:
            if linea.strip() == '\\.':
                excluir_copy = False
            continue
        
        # Si estamos en un bloque excluido, continuar
        if excluir_bloque:
            # Detectar fin del bloque
            if '--' in linea and 'TOC entry' in linea and tabla_excluir not in linea:
                excluir_bloque = False
            elif linea.strip().startswith('CREATE') and tabla_excluir not in linea:
                excluir_bloque = False
            else:
                i += 1
                continue
        
        lineas_filtradas.append(linea)
        i += 1
    
    # Escribir archivo filtrado
    contenido_filtrado = '\n'.join(lineas_filtradas)
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write(contenido_filtrado)
    
    tamaño_filtrado = len(contenido_filtrado)
    print(f"\n[+] Archivo SQL limpiado guardado: {sql_file}")
    print(f"[+] Tamaño original: {tamaño_original:,} bytes")
    print(f"[+] Tamaño filtrado: {tamaño_filtrado:,} bytes")
    print(f"[+] Reducción: {tamaño_original - tamaño_filtrado:,} bytes")
    
    return True

def main():
    sql_file = r"C:\Users\User\Downloads\BASEDEHORAIO_PARA_SUPABASE.sql"
    
    if limpiar_tabla_del_sql(sql_file):
        print("\n" + "=" * 70)
        print("  LIMPIEZA COMPLETADA")
        print("=" * 70)
        print(f"\n✅ Archivo SQL limpiado: {sql_file}")
        print("\n📝 Ahora puedes ejecutar este archivo en Supabase SQL Editor")
    else:
        print("\n❌ La limpieza falló.")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

