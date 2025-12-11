#!/usr/bin/env python
"""
Script para migrar datos desde la base de datos local a Supabase usando Django ORM.
Lee datos de la BD local e inserta en Supabase.
"""

import os
import sys
import django
from pathlib import Path
from decouple import config

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la_pontificia_horarios.settings')
django.setup()

from django.db import transaction
from django.conf import settings
import psycopg2
from psycopg2.extras import RealDictCursor

# Importar modelos
from django.contrib.auth.models import User
from apps.academic_setup.models import (
    TipoUnidadAcademica, UnidadAcademica, Carrera, Ciclo, Seccion,
    PeriodoAcademico, TiposEspacio, EspaciosFisicos, Especialidades,
    Materias, CarreraMaterias, MateriaEspecialidadesRequeridas
)
from apps.users.models import Roles, Docentes, DocenteEspecialidades, SesionesUsuario
from apps.scheduling.models import (
    Grupos, BloquesHorariosDefinicion, DisponibilidadDocentes,
    ConfiguracionRestricciones
)
# NO importar HorariosAsignados según solicitud

def get_local_connection():
    """Obtener conexión a la base de datos local (hardcodeada)"""
    # Configuración de la BD local (no Supabase)
    local_config = {
        'HOST': 'localhost',
        'PORT': '5434',
        'NAME': 'Sistemaponti',
        'USER': 'postgres',
        'PASSWORD': config('DB_PASSWORD_LOCAL', default='')  # Opcional: agregar a .env
    }
    
    # Conectar con encoding SQL_ASCII para evitar problemas
    import os as os_module
    original_encoding = os_module.environ.get('PGCLIENTENCODING', None)
    try:
        os_module.environ['PGCLIENTENCODING'] = 'SQL_ASCII'
        conn = psycopg2.connect(
            host=local_config['HOST'],
            port=local_config['PORT'],
            database=local_config['NAME'],
            user=local_config['USER'],
            password=local_config['PASSWORD'],
            connect_timeout=10
        )
        try:
            conn.set_client_encoding('LATIN1')
        except:
            conn.set_client_encoding('SQL_ASCII')
        return conn
    finally:
        if original_encoding:
            os_module.environ['PGCLIENTENCODING'] = original_encoding
        elif 'PGCLIENTENCODING' in os_module.environ:
            del os_module.environ['PGCLIENTENCODING']

def clean_encoding(value):
    """Limpiar problemas de encoding"""
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return value.encode('latin1', errors='replace').decode('utf-8', errors='replace')
        except:
            return value.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    return value

def migrar_tabla(conn_local, tabla_modelo, tabla_sql, order_by=None, exclude_table=False):
    """
    Migrar datos de una tabla desde local a Supabase usando Django ORM
    
    Args:
        conn_local: Conexión a BD local
        tabla_modelo: Modelo de Django
        tabla_sql: Nombre de la tabla en SQL
        order_by: Campo para ordenar
        exclude_table: Si True, no migrar esta tabla
    """
    if exclude_table:
        print(f"   [!] Saltando tabla: {tabla_sql} (excluida)")
        return 0
    
    print(f"\n[*] Migrando {tabla_sql}...")
    
    try:
        # Leer datos de la BD local
        with conn_local.cursor(cursor_factory=RealDictCursor) as cursor:
            order_clause = f"ORDER BY {order_by}" if order_by else ""
            query = f"SELECT * FROM {tabla_sql} {order_clause}"
            cursor.execute(query)
            rows = cursor.fetchall()
        
        if not rows:
            print(f"   [!] Sin datos")
            return 0
        
        print(f"   [+] {len(rows)} registros encontrados")
        
        # Limpiar datos existentes en Supabase (opcional)
        tabla_modelo.objects.all().delete()
        print(f"   [*] Datos existentes eliminados en Supabase")
        
        # Insertar en lotes
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            objetos = []
            
            for row in batch:
                # Limpiar encoding
                cleaned_row = {}
                for key, value in row.items():
                    cleaned_row[key] = clean_encoding(value)
                
                try:
                    # Crear objeto del modelo
                    obj = tabla_modelo(**cleaned_row)
                    objetos.append(obj)
                except Exception as e:
                    print(f"   [-] Error creando objeto: {e}")
                    print(f"      Datos: {cleaned_row}")
                    continue
            
            # Insertar en lote
            if objetos:
                try:
                    tabla_modelo.objects.bulk_create(objetos, ignore_conflicts=True)
                    total_inserted += len(objetos)
                    print(f"   [*] Insertados {total_inserted}/{len(rows)} registros...", end='\r')
                except Exception as e:
                    print(f"\n   [-] Error en bulk_create: {e}")
                    # Intentar uno por uno
                    for obj in objetos:
                        try:
                            obj.save()
                            total_inserted += 1
                        except Exception as e2:
                            print(f"   [-] Error insertando registro: {e2}")
        
        print(f"\n   [+] {total_inserted} registros migrados exitosamente")
        return total_inserted
        
    except Exception as e:
        print(f"   [-] Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    print("\n" + "=" * 70)
    print("  MIGRAR DATOS DE BASE LOCAL A SUPABASE USANDO DJANGO")
    print("=" * 70 + "\n")
    
    # Verificar configuración
    db_config_supabase = settings.DATABASES['default']
    print(f"[*] Base de datos local: localhost:5434/Sistemaponti")
    print(f"[*] Base de datos destino (Supabase): {db_config_supabase['HOST']}:{db_config_supabase['PORT']}/{db_config_supabase['NAME']}")
    
    # Verificar que estamos conectados a Supabase
    if 'supabase.co' not in db_config_supabase.get('HOST', ''):
        print("\n⚠️  ADVERTENCIA: No estás conectado a Supabase")
        print("   Cambia la configuración en .env para apuntar a Supabase")
        print("   O ejecuta: .\\scripts\\cambiar_a_supabase.ps1")
        respuesta = input("\n¿Continuar de todas formas? (s/n): ")
        if respuesta.lower() != 's':
            return
    
    print()
    
    # Conectar a BD local
    print("[*] Conectando a base de datos local...")
    conn_local = get_local_connection()
    print("[+] Conectado\n")
    
    try:
        total_migrados = 0
        
        # 1. auth_user
        total_migrados += migrar_tabla(conn_local, User, 'auth_user', 'id')
        
        # 2. TipoUnidadAcademica
        total_migrados += migrar_tabla(conn_local, TipoUnidadAcademica, 'academic_setup_tipounidadacademica', 'tipo_unidad_id')
        
        # 3. UnidadAcademica
        total_migrados += migrar_tabla(conn_local, UnidadAcademica, 'academic_setup_unidadacademica', 'unidad_id')
        
        # 4. TiposEspacio
        total_migrados += migrar_tabla(conn_local, TiposEspacio, 'academic_setup_tiposespacio', 'tipo_espacio_id')
        
        # 5. Especialidades
        total_migrados += migrar_tabla(conn_local, Especialidades, 'academic_setup_especialidades', 'especialidad_id')
        
        # 6. Carrera
        total_migrados += migrar_tabla(conn_local, Carrera, 'academic_setup_carrera', 'carrera_id')
        
        # 7. Ciclo
        total_migrados += migrar_tabla(conn_local, Ciclo, 'academic_setup_ciclo', 'ciclo_id')
        
        # 8. Seccion
        total_migrados += migrar_tabla(conn_local, Seccion, 'academic_setup_seccion', 'seccion_id')
        
        # 9. PeriodoAcademico
        total_migrados += migrar_tabla(conn_local, PeriodoAcademico, 'academic_setup_periodoacademico', 'periodo_id')
        
        # 10. EspaciosFisicos
        total_migrados += migrar_tabla(conn_local, EspaciosFisicos, 'academic_setup_espaciosfisicos', 'espacio_id')
        
        # 11. Materias
        total_migrados += migrar_tabla(conn_local, Materias, 'academic_setup_materias', 'materia_id')
        
        # 12. CarreraMaterias
        total_migrados += migrar_tabla(conn_local, CarreraMaterias, 'academic_setup_carreramaterias')
        
        # 13. MateriaEspecialidadesRequeridas
        total_migrados += migrar_tabla(conn_local, MateriaEspecialidadesRequeridas, 'academic_setup_materiaespecialidadesrequeridas')
        
        # 14. Roles
        total_migrados += migrar_tabla(conn_local, Roles, 'users_roles', 'rol_id')
        
        # 15. Docentes
        total_migrados += migrar_tabla(conn_local, Docentes, 'users_docentes', 'docente_id')
        
        # 16. DocenteEspecialidades
        total_migrados += migrar_tabla(conn_local, DocenteEspecialidades, 'users_docenteespecialidades')
        
        # 17. SesionesUsuario
        total_migrados += migrar_tabla(conn_local, SesionesUsuario, 'users_sesionesusuario')
        
        # 18. BloquesHorariosDefinicion
        total_migrados += migrar_tabla(conn_local, BloquesHorariosDefinicion, 'scheduling_bloqueshorariosdefinicion', 'bloque_def_id')
        
        # 19. Grupos
        total_migrados += migrar_tabla(conn_local, Grupos, 'scheduling_grupos', 'grupo_id')
        
        # 20. Grupos.materias (many-to-many)
        print(f"\n[*] Migrando relación many-to-many: scheduling_grupos_materias...")
        try:
            with conn_local.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM scheduling_grupos_materias")
                relaciones = cursor.fetchall()
            
            if relaciones:
                print(f"   [+] {len(relaciones)} relaciones encontradas")
                # Migrar relaciones usando el ORM de Django
                for rel in relaciones:
                    try:
                        grupo_id = rel['grupos_id']
                        materia_id = rel['materias_id']
                        grupo = Grupos.objects.get(grupo_id=grupo_id)
                        materia = Materias.objects.get(materia_id=materia_id)
                        grupo.materias.add(materia)
                    except Exception as e:
                        print(f"   [-] Error agregando relación grupo_id={grupo_id}, materia_id={materia_id}: {e}")
                
                print(f"   [+] Relaciones many-to-many migradas")
                total_migrados += len(relaciones)
            else:
                print(f"   [!] Sin relaciones")
        except Exception as e:
            print(f"   [-] Error: {e}")
        
        # 21. DisponibilidadDocentes
        total_migrados += migrar_tabla(conn_local, DisponibilidadDocentes, 'scheduling_disponibilidaddocentes', 'disponibilidad_id')
        
        # 22. ConfiguracionRestricciones
        total_migrados += migrar_tabla(conn_local, ConfiguracionRestricciones, 'scheduling_configuracionrestricciones', 'restriccion_id')
        
        # NO migrar HorariosAsignados (según solicitud)
        print("\n[!] HorariosAsignados NO migrado (según solicitud)")
        
        print("\n" + "=" * 70)
        print("  MIGRACIÓN COMPLETADA")
        print("=" * 70)
        print(f"\n✅ Total de registros migrados: {total_migrados}")
        print("\n📝 Verifica los datos en Supabase")
        
    finally:
        conn_local.close()
        print("\n[*] Conexión local cerrada")

if __name__ == '__main__':
    main()

