#!/usr/bin/env python
"""
Script para exportar datos configurando el encoding de PostgreSQL antes de exportar.
Esto puede resolver problemas de encoding en la base de datos.
"""

import os
import sys
import django
from pathlib import Path
import subprocess
from datetime import datetime

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la_pontificia_horarios.settings')
django.setup()

from django.conf import settings
from django.db import connection

def fix_database_encoding():
    """Configurar encoding UTF-8 en la conexión de PostgreSQL"""
    try:
        with connection.cursor() as cursor:
            # Forzar encoding UTF-8
            cursor.execute("SET client_encoding TO 'UTF8'")
            cursor.execute("SHOW client_encoding")
            encoding = cursor.fetchone()
            print(f"✅ Encoding configurado: {encoding[0] if encoding else 'UTF8'}")
            return True
    except Exception as e:
        print(f"⚠️  No se pudo configurar encoding: {e}")
        return False

def export_with_encoding_fix():
    """Exportar datos con encoding corregido"""
    print("\n" + "=" * 60)
    print("  EXPORTAR CON CORRECCIÓN DE ENCODING")
    print("=" * 60 + "\n")
    
    db_config = settings.DATABASES['default']
    print(f"📊 Base de datos: {db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}\n")
    
    # Configurar encoding
    print("🔧 Configurando encoding de la base de datos...")
    fix_database_encoding()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"backup_sin_horarios_{timestamp}.json"
    
    print(f"\n📦 Exportando a: {output_file}")
    print("⏳ Esto puede tardar varios minutos...\n")
    
    # Usar subprocess con variables de entorno para forzar UTF-8
    env = os.environ.copy()
    env['PGCLIENTENCODING'] = 'UTF8'
    env['PYTHONIOENCODING'] = 'utf-8'
    
    try:
        manage_py = str(BASE_DIR / 'manage.py')
        result = subprocess.run(
            [sys.executable, manage_py, 'dumpdata',
             '--natural-foreign', '--natural-primary',
             '--exclude', 'scheduling.HorariosAsignados',
             '--indent', '2'],
            capture_output=True,
            text=False,
            cwd=str(BASE_DIR),
            env=env
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='replace')
            print(f"❌ Error: {error_msg[:500]}")
            
            # Intentar identificar el problema
            if '0xf3' in error_msg or 'invalid continuation byte' in error_msg:
                print("\n💡 El problema parece ser datos con encoding incorrecto en la BD")
                print("   Opciones:")
                print("   1. Usar pg_dump directamente (ver scripts/exportar_con_pg_dump.md)")
                print("   2. Limpiar/corregir datos problemáticos en la base de datos")
                print("   3. Exportar solo las apps que funcionan")
            return False
        
        # Decodificar con manejo de errores
        print("🔧 Decodificando datos...")
        content = result.stdout.decode('utf-8', errors='replace')
        
        # Escribir archivo
        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            f.write(content)
        
        file_size = Path(output_file).stat().st_size / (1024 * 1024)
        print(f"\n✅ Exportación completada!")
        print(f"📁 Archivo: {output_file}")
        print(f"📊 Tamaño: {file_size:.2f} MB")
        print(f"\n⚠️  NOTA: HorariosAsignados NO fue incluido")
        print(f"\n💡 Próximo paso: Importar a Supabase")
        print(f"   python scripts/importar_datos_supabase.py --file {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    export_with_encoding_fix()

