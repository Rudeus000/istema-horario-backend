#!/usr/bin/env python
"""
Script para exportar datos usando COPY TO de PostgreSQL directamente.
Esto evita problemas de encoding porque PostgreSQL maneja la conversión.
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime
import psycopg2
from django.conf import settings

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la_pontificia_horarios.settings')
django.setup()

def escape_sql_string(value):
    """Escapar string para SQL"""
    if value is None or value == '':
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        # Escapar comillas simples y limpiar
        cleaned = value.replace("'", "''").replace('\n', ' ').replace('\r', ' ')
        return f"'{cleaned}'"
    return 'NULL'

def export_table_to_sql(table_name, columns, csv_file, sql_lines, primary_key=None):
    """Leer CSV y generar INSERTs SQL"""
    import csv
    
    try:
        with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if not rows:
            return 0
        
        sql_lines.append(f"\n-- Tabla: {table_name} ({len(rows)} registros)")
        
        # Ordenar si hay primary_key
        if primary_key and primary_key in columns:
            try:
                rows = sorted(rows, key=lambda x: int(x.get(primary_key, 0)) if x.get(primary_key, '').isdigit() else 0)
            except:
                pass
        
        # Generar INSERTs
        for row in rows:
            values = [escape_sql_string(row.get(col, '')) for col in columns]
            columns_str = ', '.join(columns)
            values_str = ', '.join(values)
            sql_lines.append(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});")
        
        return len(rows)
    except Exception as e:
        print(f"      [-] Error procesando CSV: {e}")
        return 0

def main():
    print("\n" + "=" * 70)
    print("  EXPORTAR DATOS USANDO COPY TO (PostgreSQL)")
    print("=" * 70 + "\n")
    
    db_config = settings.DATABASES['default']
    print(f"[*] Base de datos: {db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"inserts_supabase_{timestamp}.sql"
    temp_dir = Path(BASE_DIR) / 'temp_export'
    temp_dir.mkdir(exist_ok=True)
    
    print(f"[*] Generando archivo SQL: {output_file}\n")
    
    sql_content = []
    sql_content.append("-- ============================================")
    sql_content.append("-- Script SQL para insertar datos en Supabase")
    sql_content.append(f"-- Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_content.append("-- ============================================")
    sql_content.append("")
    sql_content.append("SET client_encoding TO 'UTF8';")
    sql_content.append("")
    
    # Conectar a PostgreSQL
    conn = psycopg2.connect(
        host=db_config['HOST'],
        port=db_config['PORT'],
        database=db_config['NAME'],
        user=db_config['USER'],
        password=db_config['PASSWORD']
    )
    
    # Tablas a exportar en orden
    tables_config = [
        ('auth_user', 'id'),
        ('academic_setup_tipounidadacademica', 'tipo_unidad_id'),
        ('academic_setup_unidadacademica', 'unidad_id'),
        ('academic_setup_tiposespacio', 'tipo_espacio_id'),
        ('academic_setup_especialidades', 'especialidad_id'),
        ('academic_setup_carrera', 'carrera_id'),
        ('academic_setup_ciclo', 'ciclo_id'),
        ('academic_setup_seccion', 'seccion_id'),
        ('academic_setup_periodoacademico', 'periodo_id'),
        ('academic_setup_materias', 'materia_id'),
        ('academic_setup_espaciosfisicos', 'espacio_id'),
        ('users_roles', 'rol_id'),
        ('users_docentes', 'docente_id'),
        ('academic_setup_carreramaterias', None),
        ('academic_setup_materiaespecialidadesrequeridas', None),
        ('users_docenteespecialidades', None),
        ('scheduling_bloqueshorariosdefinicion', 'bloque_def_id'),
        ('scheduling_grupos', 'grupo_id'),
        ('scheduling_grupos_materias', None),
        ('scheduling_disponibilidaddocentes', 'disponibilidad_id'),
        ('scheduling_configuracionrestricciones', 'restriccion_id'),
        ('users_sesionesusuario', 'sesion_id'),
    ]
    
    try:
        with conn.cursor() as cursor:
            for table_name, primary_key in tables_config:
                print(f"[*] Exportando {table_name}...", end=" ")
                
                # Obtener columnas
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)
                columns = [row[0] for row in cursor.fetchall()]
                
                if not columns:
                    print("[-] Tabla no existe o sin columnas")
                    continue
                
                # Exportar usando COPY TO
                csv_file = temp_dir / f"{table_name}.csv"
                try:
                    cursor.execute(f"""
                        COPY (SELECT * FROM {table_name} {'ORDER BY ' + primary_key if primary_key else ''}) 
                        TO STDOUT WITH CSV HEADER ENCODING 'UTF8'
                    """)
                    
                    with open(csv_file, 'w', encoding='utf-8', errors='replace') as f:
                        # psycopg2 copy_to escribe directamente
                        import io
                        buffer = io.StringIO()
                        cursor.copy_expert(f"""
                            COPY (SELECT * FROM {table_name} {'ORDER BY ' + primary_key if primary_key else ''}) 
                            TO STDOUT WITH CSV HEADER ENCODING 'UTF8'
                        """, buffer)
                        buffer.seek(0)
                        f.write(buffer.getvalue())
                    
                    # Procesar CSV y generar SQL
                    count = export_table_to_sql(table_name, columns, csv_file, sql_content, primary_key)
                    print(f"[+] {count} registros")
                    
                    # Eliminar CSV temporal
                    csv_file.unlink()
                    
                except Exception as e:
                    print(f"[-] Error: {e}")
                    continue
    
    finally:
        conn.close()
    
    # Escribir archivo SQL
    print(f"\n[*] Escribiendo archivo SQL: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
        f.write('\n'.join(sql_content))
    
    file_size = Path(output_file).stat().st_size / (1024 * 1024)
    print(f"\n[+] Archivo SQL generado exitosamente!")
    print(f"[*] Archivo: {output_file}")
    print(f"[*] Tamaño: {file_size:.2f} MB")
    print(f"\n[*] Proximo paso:")
    print(f"   1. Abre Supabase SQL Editor")
    print(f"   2. Copia y pega el contenido de {output_file}")
    print(f"   3. Ejecuta el script")
    print(f"\n[!] NOTA: HorariosAsignados NO fue incluido")
    
    # Limpiar directorio temporal
    try:
        temp_dir.rmdir()
    except:
        pass

if __name__ == '__main__':
    main()

