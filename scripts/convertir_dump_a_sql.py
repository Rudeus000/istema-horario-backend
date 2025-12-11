#!/usr/bin/env python
"""
Script para convertir un dump de PostgreSQL (formato custom) a SQL plano
y excluir la tabla scheduling_horariosasignados según solicitud del usuario.
"""

import subprocess
import sys
from pathlib import Path

def convertir_dump_a_sql(dump_file, output_file, excluir_tablas=None):
    """
    Convierte un dump custom de PostgreSQL a SQL plano
    
    Args:
        dump_file: Ruta al archivo dump (.backup o .sql en formato custom)
        output_file: Ruta donde guardar el SQL plano
        excluir_tablas: Lista de tablas a excluir (opcional)
    """
    if excluir_tablas is None:
        excluir_tablas = ['scheduling_horariosasignados']
    
    print("\n" + "=" * 70)
    print("  CONVERTIR DUMP CUSTOM A SQL PLANO")
    print("=" * 70 + "\n")
    
    dump_path = Path(dump_file)
    if not dump_path.exists():
        print(f"❌ Error: El archivo {dump_file} no existe")
        return False
    
    print(f"[*] Archivo dump: {dump_file}")
    print(f"[*] Tamaño: {dump_path.stat().st_size / 1024:.2f} KB")
    print(f"[*] Tablas a excluir: {', '.join(excluir_tablas)}")
    print()
    
    # Buscar pg_restore en las rutas comunes de PostgreSQL
    posibles_rutas = [
        r'C:\Program Files\PostgreSQL\17\bin\pg_restore.exe',
        r'C:\Program Files\PostgreSQL\16\bin\pg_restore.exe',
        r'C:\Program Files\PostgreSQL\15\bin\pg_restore.exe',
        r'C:\Program Files\PostgreSQL\14\bin\pg_restore.exe',
        'pg_restore'  # Intentar desde PATH
    ]
    
    pg_restore_path = None
    for ruta in posibles_rutas:
        if ruta == 'pg_restore':
            # Intentar desde PATH
            try:
                result = subprocess.run(['where', 'pg_restore'], capture_output=True, text=True)
                if result.returncode == 0:
                    pg_restore_path = 'pg_restore'
                    break
            except:
                pass
        elif Path(ruta).exists():
            pg_restore_path = ruta
            break
    
    if not pg_restore_path:
        print("❌ Error: pg_restore no encontrado.")
        print("   Asegúrate de que PostgreSQL esté instalado")
        print("   Rutas buscadas:")
        for ruta in posibles_rutas:
            if ruta != 'pg_restore':
                print(f"     - {ruta}")
        return False
    
    # Comando pg_restore para convertir a SQL plano
    # pg_restore genera SQL plano cuando el archivo de salida es .sql
    # Usamos --no-owner y --no-privileges para evitar problemas en Supabase
    cmd = [
        pg_restore_path,
        '--file', str(output_file),
        '--no-owner',  # No incluir comandos de ownership
        '--no-privileges',  # No incluir comandos de privilegios
        '--verbose',
        str(dump_file)
    ]
    
    print(f"[*] Usando: {pg_restore_path}")
    print(f"[*] Ejecutando conversión...\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("[+] Conversión exitosa!")
        print(f"[+] Archivo SQL generado: {output_file}")
        
        # Ahora necesitamos filtrar las tablas excluidas del SQL
        if excluir_tablas:
            print(f"\n[*] Filtrando tablas excluidas...")
            filtrar_tablas_del_sql(output_file, excluir_tablas)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar pg_restore:")
        print(f"   {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Error: No se pudo ejecutar pg_restore.")
        return False

def filtrar_tablas_del_sql(sql_file, tablas_excluir):
    """
    Filtra las tablas excluidas del archivo SQL
    """
    sql_path = Path(sql_file)
    
    # Leer el archivo SQL
    with open(sql_path, 'r', encoding='utf-8', errors='replace') as f:
        contenido = f.read()
    
    # Crear backup
    backup_file = sql_path.with_suffix('.sql.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print(f"[*] Backup creado: {backup_file}")
    
    # Filtrar líneas relacionadas con las tablas excluidas
    lineas = contenido.split('\n')
    lineas_filtradas = []
    excluir_bloque = False
    excluir_copy = False
    tabla_actual = None
    en_definicion_tabla = False
    nivel_parentesis = 0
    
    for i, linea in enumerate(lineas):
        # Detectar inicio de bloque de tabla (comentarios TOC o CREATE TABLE)
        for tabla in tablas_excluir:
            # Detectar en comentarios TOC
            if f'Name: {tabla};' in linea or f'Name: {tabla}' in linea:
                excluir_bloque = True
                tabla_actual = tabla
                en_definicion_tabla = True
                print(f"   [-] Excluyendo tabla: {tabla}")
                continue
            # Detectar CREATE TABLE
            if f'CREATE TABLE public.{tabla}' in linea:
                excluir_bloque = True
                tabla_actual = tabla
                en_definicion_tabla = True
                print(f"   [-] Excluyendo tabla: {tabla}")
                continue
        
        # Si estamos excluyendo un bloque
        if excluir_bloque:
            # Contar paréntesis para detectar fin de definición de tabla
            if en_definicion_tabla:
                nivel_parentesis += linea.count('(') - linea.count(')')
                # Si encontramos un punto y coma después de cerrar paréntesis, terminó la definición
                if nivel_parentesis <= 0 and ');' in linea:
                    en_definicion_tabla = False
                    nivel_parentesis = 0
                    # Continuar excluyendo hasta el siguiente bloque importante
                    continue
            
            # Detectar fin de bloque (nuevo TOC entry o CREATE importante)
            if linea.strip().startswith('--') and 'TOC entry' in linea and tabla_actual not in linea:
                # Verificar si es el inicio de otra tabla
                es_otra_tabla = True
                for tabla in tablas_excluir:
                    if tabla in linea:
                        es_otra_tabla = False
                        break
                if es_otra_tabla:
                    excluir_bloque = False
                    tabla_actual = None
                    en_definicion_tabla = False
                    nivel_parentesis = 0
                    # No continuar, procesar esta línea normalmente
                else:
                    continue
            
            # Continuar excluyendo si aún estamos en un bloque de la tabla
            if tabla_actual and (tabla_actual in linea or en_definicion_tabla):
                continue
            
            # Si llegamos aquí y no hay tabla_actual, terminamos de excluir
            if not tabla_actual:
                excluir_bloque = False
        
        # Excluir comandos COPY para las tablas excluidas
        if any(f'COPY public.{tabla}' in linea for tabla in tablas_excluir):
            # Excluir también las líneas siguientes hasta encontrar \.
            excluir_copy = True
            continue
        
        if excluir_copy:
            if linea.strip() == '\\.':
                excluir_copy = False
            continue
        
        # Excluir comandos ALTER TABLE, CREATE INDEX, CREATE SEQUENCE para las tablas excluidas
        if any(f'ALTER TABLE ONLY public.{tabla}' in linea or 
               f'CREATE INDEX' in linea and tabla in linea or
               f'CREATE SEQUENCE' in linea and tabla in linea or
               f'SEQUENCE SET' in linea and tabla in linea or
               f'setval' in linea and tabla in linea
               for tabla in tablas_excluir):
            continue
        
        # Excluir constraints que mencionan la tabla
        if any(f'CONSTRAINT' in linea and tabla in linea for tabla in tablas_excluir):
            continue
        
        lineas_filtradas.append(linea)
    
    # Escribir archivo filtrado
    contenido_filtrado = '\n'.join(lineas_filtradas)
    with open(sql_path, 'w', encoding='utf-8') as f:
        f.write(contenido_filtrado)
    
    print(f"[+] Archivo SQL filtrado guardado: {sql_file}")
    print(f"[+] Tamaño original: {len(contenido)} bytes")
    print(f"[+] Tamaño filtrado: {len(contenido_filtrado)} bytes")

def main():
    dump_file = r"C:\Users\User\Downloads\BASEDEHORAIO.sql"
    output_file = r"C:\Users\User\Downloads\BASEDEHORAIO_PARA_SUPABASE.sql"
    
    if len(sys.argv) > 1:
        dump_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    exito = convertir_dump_a_sql(
        dump_file,
        output_file,
        excluir_tablas=['scheduling_horariosasignados']
    )
    
    if exito:
        print("\n" + "=" * 70)
        print("  CONVERSIÓN COMPLETADA")
        print("=" * 70)
        print(f"\n✅ Archivo SQL listo: {output_file}")
        print("\n📝 Próximos pasos:")
        print("   1. Abre Supabase SQL Editor")
        print("   2. Asegúrate de haber ejecutado create_supabase_database.sql primero")
        print("   3. Abre el archivo SQL generado")
        print("   4. Ejecuta el script en Supabase")
        print("\n⚠️  NOTA: La tabla 'scheduling_horariosasignados' fue excluida")
    else:
        print("\n❌ La conversión falló. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == '__main__':
    main()

