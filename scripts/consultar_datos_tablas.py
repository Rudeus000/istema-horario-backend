#!/usr/bin/env python
"""
Script simple para consultar y mostrar qué datos tiene cada tabla.
Solo muestra conteos y algunos ejemplos, sin intentar exportar.
"""

import os
import sys
import django
from pathlib import Path
from django.conf import settings

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la_pontificia_horarios.settings')
django.setup()

from django.db import connection

def main():
    print("\n" + "=" * 70)
    print("  CONSULTAR DATOS EN TABLAS")
    print("=" * 70 + "\n")
    
    db_config = settings.DATABASES['default']
    print(f"[*] Base de datos: {db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}\n")
    
    tables = [
        'auth_user',
        'academic_setup_tipounidadacademica',
        'academic_setup_unidadacademica',
        'academic_setup_tiposespacio',
        'academic_setup_especialidades',
        'academic_setup_carrera',
        'academic_setup_ciclo',
        'academic_setup_seccion',
        'academic_setup_periodoacademico',
        'academic_setup_materias',
        'academic_setup_espaciosfisicos',
        'users_roles',
        'users_docentes',
        'academic_setup_carreramaterias',
        'academic_setup_materiaespecialidadesrequeridas',
        'users_docenteespecialidades',
        'scheduling_bloqueshorariosdefinicion',
        'scheduling_grupos',
        'scheduling_grupos_materias',
        'scheduling_disponibilidaddocentes',
        'scheduling_configuracionrestricciones',
        'users_sesionesusuario',
        'scheduling_horariosasignados',  # Solo para mostrar que existe
    ]
    
    print("[*] Consultando tablas...\n")
    
    results = {}
    
    with connection.cursor() as cursor:
        for table in tables:
            try:
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                # Obtener columnas
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = [row[0] for row in cursor.fetchall()]
                
                results[table] = {
                    'count': count,
                    'columns': columns
                }
                
                status = "[+]" if count > 0 else "[!]"
                print(f"{status} {table}: {count} registros ({len(columns)} columnas)")
                
            except Exception as e:
                print(f"[-] {table}: Error - {e}")
                results[table] = {'error': str(e)}
    
    # Generar resumen
    print("\n" + "=" * 70)
    print("  RESUMEN")
    print("=" * 70 + "\n")
    
    total_tables = len([t for t in tables if 'error' not in results.get(t, {})])
    total_records = sum([r.get('count', 0) for r in results.values() if 'error' not in r])
    
    print(f"[*] Total de tablas consultadas: {total_tables}")
    print(f"[*] Total de registros: {total_records}")
    print(f"\n[!] HorariosAsignados tiene {results.get('scheduling_horariosasignados', {}).get('count', 0)} registros (NO se exportará)")
    
    # Guardar resumen en archivo
    summary_file = "resumen_tablas.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("RESUMEN DE DATOS EN BASE DE DATOS\n")
        f.write("=" * 70 + "\n\n")
        for table, data in results.items():
            if 'error' in data:
                f.write(f"{table}: ERROR - {data['error']}\n")
            else:
                f.write(f"{table}: {data['count']} registros\n")
                f.write(f"  Columnas: {', '.join(data['columns'][:5])}{'...' if len(data['columns']) > 5 else ''}\n")
        f.write(f"\nTotal registros: {total_records}\n")
    
    print(f"\n[+] Resumen guardado en: {summary_file}")

if __name__ == '__main__':
    main()

