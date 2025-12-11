#!/usr/bin/env python
"""
Script para consultar la base de datos local y generar un archivo SQL con INSERTs
para insertar los datos en Supabase.
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from django.conf import settings
import traceback

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la_pontificia_horarios.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User

def escape_sql_string(value):
    """Escapar string para SQL"""
    if value is None:
        return 'NULL'
    if isinstance(value, bool):
        return 'TRUE' if value else 'FALSE'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, datetime):
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
    if isinstance(value, str):
        # Limpiar encoding problemático
        try:
            cleaned = value.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            # Escapar comillas simples
            cleaned = cleaned.replace("'", "''")
            return f"'{cleaned}'"
        except:
            return "''"
    return 'NULL'

def get_table_data(table_name, order_by=None):
    """Obtener todos los datos de una tabla"""
    db_config = settings.DATABASES['default']
    
    # Conectar y manejar encoding
    # Guardar encoding original
    original_encoding = os.environ.get('PGCLIENTENCODING', None)
    try:
        # Intentar establecer SQL_ASCII antes de conectar para evitar problemas
        os.environ['PGCLIENTENCODING'] = 'SQL_ASCII'
        conn = psycopg2.connect(
            host=db_config['HOST'],
            port=db_config['PORT'],
            database=db_config['NAME'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            connect_timeout=10
        )
        # Establecer encoding después de conectar
        try:
            conn.set_client_encoding('LATIN1')
        except:
            conn.set_client_encoding('SQL_ASCII')
    finally:
        # Restaurar encoding original
        if original_encoding:
            os.environ['PGCLIENTENCODING'] = original_encoding
        elif 'PGCLIENTENCODING' in os.environ:
            del os.environ['PGCLIENTENCODING']
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            order_clause = f"ORDER BY {order_by}" if order_by else ""
            query = f"SELECT * FROM {table_name} {order_clause}"
            cursor.execute(query)
            rows = cursor.fetchall()
            # Convertir a lista de diccionarios limpiando encoding
            result = []
            for row in rows:
                cleaned_row = {}
                for key, value in row.items():
                    if isinstance(value, str):
                        # Convertir de latin1 a UTF-8 limpiando caracteres inválidos
                        try:
                            # Primero codificar como latin1 (que acepta cualquier byte)
                            # Luego decodificar como UTF-8
                            cleaned_row[key] = value.encode('latin1', errors='replace').decode('utf-8', errors='replace')
                        except Exception as e:
                            # Si falla, usar replace para limpiar
                            cleaned_row[key] = value.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                    elif isinstance(value, bytes):
                        try:
                            cleaned_row[key] = value.decode('latin1', errors='replace').encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                        except:
                            cleaned_row[key] = value.decode('utf-8', errors='replace')
                    else:
                        cleaned_row[key] = value
                result.append(cleaned_row)
            return result
    finally:
        conn.close()

def generate_insert_sql(table_name, data, primary_key=None):
    """Generar SQL INSERT para una tabla"""
    if not data:
        return []
    
    sql_lines = []
    sql_lines.append(f"\n-- Tabla: {table_name} ({len(data)} registros)")
    
    # Obtener columnas del primer registro
    columns = list(data[0].keys())
    
    # Si hay primary_key, ordenar por ella
    if primary_key and primary_key in columns:
        data = sorted(data, key=lambda x: x[primary_key] or 0)
    
    # Generar INSERTs
    for row in data:
        values = [escape_sql_string(row[col]) for col in columns]
        columns_str = ', '.join(columns)
        values_str = ', '.join(values)
        sql_lines.append(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});")
    
    return sql_lines

def get_many_to_many_data(table_name, fk1_col, fk2_col):
    """Obtener datos de tablas many-to-many"""
    db_config = settings.DATABASES['default']
    
    # Conectar y manejar encoding
    # Guardar encoding original
    original_encoding = os.environ.get('PGCLIENTENCODING', None)
    try:
        # Intentar establecer SQL_ASCII antes de conectar para evitar problemas
        os.environ['PGCLIENTENCODING'] = 'SQL_ASCII'
        conn = psycopg2.connect(
            host=db_config['HOST'],
            port=db_config['PORT'],
            database=db_config['NAME'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            connect_timeout=10
        )
        # Establecer encoding después de conectar
        try:
            conn.set_client_encoding('LATIN1')
        except:
            conn.set_client_encoding('SQL_ASCII')
    finally:
        # Restaurar encoding original
        if original_encoding:
            os.environ['PGCLIENTENCODING'] = original_encoding
        elif 'PGCLIENTENCODING' in os.environ:
            del os.environ['PGCLIENTENCODING']
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = f"SELECT * FROM {table_name} ORDER BY {fk1_col}, {fk2_col}"
            cursor.execute(query)
            rows = cursor.fetchall()
            # Convertir a lista de diccionarios limpiando encoding
            result = []
            for row in rows:
                cleaned_row = {}
                for key, value in row.items():
                    if isinstance(value, str):
                        try:
                            cleaned_row[key] = value.encode('latin1', errors='replace').decode('utf-8', errors='replace')
                        except Exception as e:
                            cleaned_row[key] = value.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                    elif isinstance(value, bytes):
                        try:
                            cleaned_row[key] = value.decode('latin1', errors='replace').encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                        except:
                            cleaned_row[key] = value.decode('utf-8', errors='replace')
                    else:
                        cleaned_row[key] = value
                result.append(cleaned_row)
            return result
    finally:
        conn.close()

def main():
    print("\n" + "=" * 70)
    print("  CONSULTAR BASE DE DATOS LOCAL Y GENERAR SQL PARA SUPABASE")
    print("=" * 70 + "\n")
    
    db_config = settings.DATABASES['default']
    print(f"[*] Base de datos: {db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}\n")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"inserts_supabase_{timestamp}.sql"
    
    print(f"[*] Generando archivo SQL: {output_file}\n")
    
    sql_content = []
    sql_content.append("-- ============================================")
    sql_content.append("-- Script SQL para insertar datos en Supabase")
    sql_content.append(f"-- Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_content.append("-- ============================================")
    sql_content.append("")
    sql_content.append("-- IMPORTANTE: Ejecutar este script en Supabase SQL Editor")
    sql_content.append("-- Orden de ejecución respetado para claves foráneas")
    sql_content.append("")
    
    # Configurar encoding
    sql_content.append("SET client_encoding TO 'UTF8';")
    sql_content.append("")
    
    # 1. auth_user
    print("[*] Consultando auth_user...")
    try:
        # Usar consulta directa para evitar problemas de encoding con Django ORM
        users_data = get_table_data('auth_user', 'id')
        if users_data:
            print(f"   [+] {len(users_data)} usuarios encontrados")
            sql_content.extend(generate_insert_sql('auth_user', users_data, 'id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
        print(f"   [-] Traceback completo:")
        traceback.print_exc()
    
    # 2. academic_setup_tipounidadacademica
    print("\n[*] Consultando academic_setup_tipounidadacademica...")
    try:
        data = get_table_data('academic_setup_tipounidadacademica', 'tipo_unidad_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_tipounidadacademica', data, 'tipo_unidad_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 3. academic_setup_unidadacademica
    print("\n[*] Consultando academic_setup_unidadacademica...")
    try:
        data = get_table_data('academic_setup_unidadacademica', 'unidad_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_unidadacademica', data, 'unidad_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 4. academic_setup_tiposespacio
    print("\n[*] Consultando academic_setup_tiposespacio...")
    try:
        data = get_table_data('academic_setup_tiposespacio', 'tipo_espacio_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_tiposespacio', data, 'tipo_espacio_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 5. academic_setup_especialidades
    print("\n[*] Consultando academic_setup_especialidades...")
    try:
        data = get_table_data('academic_setup_especialidades', 'especialidad_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_especialidades', data, 'especialidad_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 6. academic_setup_carrera
    print("\n[*] Consultando academic_setup_carrera...")
    try:
        data = get_table_data('academic_setup_carrera', 'carrera_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_carrera', data, 'carrera_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 7. academic_setup_ciclo
    print("\n[*] Consultando academic_setup_ciclo...")
    try:
        data = get_table_data('academic_setup_ciclo', 'ciclo_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_ciclo', data, 'ciclo_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 8. academic_setup_seccion
    print("\n[*] Consultando academic_setup_seccion...")
    try:
        data = get_table_data('academic_setup_seccion', 'seccion_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_seccion', data, 'seccion_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 9. academic_setup_periodoacademico
    print("\n[*] Consultando academic_setup_periodoacademico...")
    try:
        data = get_table_data('academic_setup_periodoacademico', 'periodo_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_periodoacademico', data, 'periodo_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 10. academic_setup_materias
    print("\n[*] Consultando academic_setup_materias...")
    try:
        data = get_table_data('academic_setup_materias', 'materia_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_materias', data, 'materia_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 11. academic_setup_espaciosfisicos
    print("\n[*] Consultando academic_setup_espaciosfisicos...")
    try:
        data = get_table_data('academic_setup_espaciosfisicos', 'espacio_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_espaciosfisicos', data, 'espacio_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 12. users_roles
    print("\n[*] Consultando users_roles...")
    try:
        data = get_table_data('users_roles', 'rol_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('users_roles', data, 'rol_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 13. users_docentes
    print("\n[*] Consultando users_docentes...")
    try:
        data = get_table_data('users_docentes', 'docente_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('users_docentes', data, 'docente_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 14. academic_setup_carreramaterias
    print("\n[*] Consultando academic_setup_carreramaterias...")
    try:
        data = get_table_data('academic_setup_carreramaterias')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_carreramaterias', data))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 15. academic_setup_materiaespecialidadesrequeridas
    print("\n[*] Consultando academic_setup_materiaespecialidadesrequeridas...")
    try:
        data = get_table_data('academic_setup_materiaespecialidadesrequeridas')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('academic_setup_materiaespecialidadesrequeridas', data))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 16. users_docenteespecialidades
    print("\n[*] Consultando users_docenteespecialidades...")
    try:
        data = get_table_data('users_docenteespecialidades')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('users_docenteespecialidades', data))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 17. scheduling_bloqueshorariosdefinicion
    print("\n[*] Consultando scheduling_bloqueshorariosdefinicion...")
    try:
        data = get_table_data('scheduling_bloqueshorariosdefinicion', 'bloque_def_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('scheduling_bloqueshorariosdefinicion', data, 'bloque_def_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 18. scheduling_grupos
    print("\n[*] Consultando scheduling_grupos...")
    try:
        data = get_table_data('scheduling_grupos', 'grupo_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('scheduling_grupos', data, 'grupo_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 19. scheduling_grupos_materias (many-to-many)
    print("\n[*] Consultando scheduling_grupos_materias (many-to-many)...")
    try:
        data = get_many_to_many_data('scheduling_grupos_materias', 'grupos_id', 'materias_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('scheduling_grupos_materias', data))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 20. scheduling_disponibilidaddocentes
    print("\n[*] Consultando scheduling_disponibilidaddocentes...")
    try:
        data = get_table_data('scheduling_disponibilidaddocentes', 'disponibilidad_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('scheduling_disponibilidaddocentes', data, 'disponibilidad_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 21. scheduling_configuracionrestricciones
    print("\n[*] Consultando scheduling_configuracionrestricciones...")
    try:
        data = get_table_data('scheduling_configuracionrestricciones', 'restriccion_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('scheduling_configuracionrestricciones', data, 'restriccion_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # 22. users_sesionesusuario
    print("\n[*] Consultando users_sesionesusuario...")
    try:
        data = get_table_data('users_sesionesusuario', 'sesion_id')
        if data:
            print(f"   [+] {len(data)} registros encontrados")
            sql_content.extend(generate_insert_sql('users_sesionesusuario', data, 'sesion_id'))
        else:
            print("   [!] Sin datos")
    except Exception as e:
        print(f"   [-] Error: {e}")
    
    # NO incluir HorariosAsignados
    print("\n[!] HorariosAsignados NO incluido (segun solicitud)")
    
    # Escribir archivo
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

if __name__ == '__main__':
    main()

