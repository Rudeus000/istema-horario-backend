#!/usr/bin/env python
"""
Script rápido para importar datos a SUPABASE.

Asegúrate de que tu .env esté configurado para Supabase antes de ejecutar.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la_pontificia_horarios.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
import argparse

def main():
    parser = argparse.ArgumentParser(description='Importar datos a Supabase')
    parser.add_argument('--file', default='backup_datos.json', help='Archivo JSON a importar')
    parser.add_argument('--flush', action='store_true', help='Limpiar datos existentes antes de importar')
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("  IMPORTANDO DATOS A SUPABASE")
    print("=" * 60 + "\n")
    
    # Verificar configuración
    db_config = settings.DATABASES['default']
    print(f"📊 Base de datos configurada:")
    print(f"   Host: {db_config['HOST']}")
    print(f"   Puerto: {db_config['PORT']}")
    print(f"   Nombre: {db_config['NAME']}")
    
    if 'supabase.co' not in db_config['HOST']:
        print("\n⚠️  ADVERTENCIA: Parece que NO estás conectado a Supabase")
        print("   Verifica tu archivo .env antes de continuar\n")
        respuesta = input("¿Continuar de todas formas? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Cancelado")
            return
    
    # Verificar archivo
    if not Path(args.file).exists():
        print(f"\n❌ Archivo no encontrado: {args.file}")
        print("\n💡 Archivos disponibles:")
        for f in Path('.').glob('backup_*.json'):
            print(f"   - {f}")
        return
    
    file_size = Path(args.file).stat().st_size / (1024 * 1024)
    print(f"\n📁 Archivo: {args.file}")
    print(f"📊 Tamaño: {file_size:.2f} MB")
    
    # Limpiar si se solicita
    if args.flush:
        print("\n⚠️  ADVERTENCIA: Se limpiarán TODOS los datos existentes")
        respuesta = input("¿Estás seguro? (escribe 'SI' para confirmar): ")
        if respuesta != 'SI':
            print("❌ Cancelado")
            return
        
        print("\n🧹 Limpiando datos existentes...")
        try:
            call_command('flush', '--noinput', verbosity=0)
            print("✅ Datos limpiados")
        except Exception as e:
            print(f"❌ Error al limpiar: {e}")
            return
    
    print(f"\n📥 Importando datos...")
    print("⏳ Esto puede tardar varios minutos...\n")
    
    try:
        call_command(
            'loaddata',
            args.file,
            verbosity=2
        )
        
        print(f"\n✅ Importación completada!")
        print(f"\n💡 Verifica los datos:")
        print(f"   python manage.py shell")
        print(f"   >>> from academic_setup.models import Carrera")
        print(f"   >>> Carrera.objects.count()")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Sugerencias:")
        print("   - Verifica que las tablas existan: python manage.py migrate")
        print("   - Si hay conflictos, usa --flush para limpiar primero")
        print("   - Revisa los errores arriba para más detalles")

if __name__ == '__main__':
    main()

