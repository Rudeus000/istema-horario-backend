#!/usr/bin/env python
"""
Script para migrar datos de base de datos local a Supabase.

Uso:
    python migrar_datos.py --export    # Exportar de local
    python migrar_datos.py --import    # Importar a Supabase
    python migrar_datos.py --full      # Exportar e importar completo
"""

import os
import sys
import django
from pathlib import Path
import json
from datetime import datetime

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la_pontificia_horarios.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
from django.db import connection

def print_header(text):
    """Imprimir encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_database_connection():
    """Verificar conexión a la base de datos"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def export_data(output_file="backup_datos.json"):
    """Exportar todos los datos de la base de datos actual"""
    print_header("EXPORTANDO DATOS")
    
    if not check_database_connection():
        print("❌ No se puede conectar a la base de datos")
        return False
    
    print(f"📦 Exportando datos a: {output_file}")
    print("⏳ Esto puede tardar varios minutos...\n")
    
    try:
        # Exportar con opciones para manejar Foreign Keys
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent', '2',
            '--output', output_file,
            verbosity=2
        )
        
        # Verificar tamaño del archivo
        file_size = Path(output_file).stat().st_size / (1024 * 1024)  # MB
        print(f"\n✅ Exportación completada!")
        print(f"📁 Archivo: {output_file}")
        print(f"📊 Tamaño: {file_size:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al exportar: {e}")
        return False

def import_data(input_file="backup_datos.json"):
    """Importar datos a la base de datos actual"""
    print_header("IMPORTANDO DATOS")
    
    if not check_database_connection():
        print("❌ No se puede conectar a la base de datos")
        return False
    
    if not Path(input_file).exists():
        print(f"❌ Archivo no encontrado: {input_file}")
        return False
    
    print(f"📥 Importando datos desde: {input_file}")
    print("⏳ Esto puede tardar varios minutos...\n")
    print("⚠️  ADVERTENCIA: Esto puede sobrescribir datos existentes\n")
    
    try:
        # Importar datos
        call_command(
            'loaddata',
            input_file,
            verbosity=2
        )
        
        print(f"\n✅ Importación completada!")
        return True
        
    except Exception as e:
        print(f"❌ Error al importar: {e}")
        print("\n💡 Sugerencias:")
        print("   - Verifica que las tablas existan (ejecuta: python manage.py migrate)")
        print("   - Si hay conflictos, limpia primero: python manage.py flush")
        return False

def show_database_info():
    """Mostrar información de la base de datos actual"""
    print_header("INFORMACIÓN DE BASE DE DATOS")
    
    db_config = settings.DATABASES['default']
    print(f"Host: {db_config['HOST']}")
    print(f"Puerto: {db_config['PORT']}")
    print(f"Base de datos: {db_config['NAME']}")
    print(f"Usuario: {db_config['USER']}")
    
    if check_database_connection():
        print("\n✅ Conexión exitosa")
        
        # Contar registros en tablas principales
        from academic_setup.models import Carrera, Materias
        from users.models import Docentes
        from scheduling.models import HorariosAsignados
        
        try:
            print(f"\n📊 Registros actuales:")
            print(f"   Carreras: {Carrera.objects.count()}")
            print(f"   Materias: {Materias.objects.count()}")
            print(f"   Docentes: {Docentes.objects.count()}")
            print(f"   Horarios: {HorariosAsignados.objects.count()}")
        except Exception as e:
            print(f"   (No se pudieron contar registros: {e})")
    else:
        print("\n❌ No se puede conectar")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrar datos entre bases de datos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Exportar datos de la base de datos actual
  python migrar_datos.py --export
  
  # Importar datos a la base de datos actual
  python migrar_datos.py --import
  
  # Ver información de la base de datos
  python migrar_datos.py --info
  
  # Especificar archivo personalizado
  python migrar_datos.py --export --file mi_backup.json
  python migrar_datos.py --import --file mi_backup.json
        """
    )
    
    parser.add_argument('--export', action='store_true', help='Exportar datos')
    parser.add_argument('--import', dest='import_data', action='store_true', help='Importar datos')
    parser.add_argument('--info', action='store_true', help='Mostrar información de BD')
    parser.add_argument('--file', default='backup_datos.json', help='Archivo de backup')
    
    args = parser.parse_args()
    
    if args.info:
        show_database_info()
    elif args.export:
        export_data(args.file)
    elif args.import_data:
        import_data(args.file)
    else:
        parser.print_help()
        print("\n💡 Tip: Usa --export para exportar o --import para importar")

if __name__ == '__main__':
    main()

