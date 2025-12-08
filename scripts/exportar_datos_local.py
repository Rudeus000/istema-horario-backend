#!/usr/bin/env python
"""
Script rápido para exportar datos de la base de datos LOCAL.

Asegúrate de que tu .env esté configurado para la base de datos LOCAL antes de ejecutar.
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
from datetime import datetime

def main():
    print("\n" + "=" * 60)
    print("  EXPORTANDO DATOS DE BASE DE DATOS LOCAL")
    print("=" * 60 + "\n")
    
    # Verificar configuración
    db_config = settings.DATABASES['default']
    print(f"📊 Base de datos configurada:")
    print(f"   Host: {db_config['HOST']}")
    print(f"   Puerto: {db_config['PORT']}")
    print(f"   Nombre: {db_config['NAME']}")
    
    if 'localhost' not in db_config['HOST'] and '127.0.0.1' not in db_config['HOST']:
        print("\n⚠️  ADVERTENCIA: Parece que NO estás conectado a la base de datos LOCAL")
        print("   Verifica tu archivo .env antes de continuar\n")
        respuesta = input("¿Continuar de todas formas? (s/n): ")
        if respuesta.lower() != 's':
            print("❌ Cancelado")
            return
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"backup_local_{timestamp}.json"
    
    print(f"\n📦 Exportando a: {output_file}")
    print("⏳ Esto puede tardar varios minutos...\n")
    
    try:
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent', '2',
            '--output', output_file,
            verbosity=2
        )
        
        # Verificar tamaño
        file_size = Path(output_file).stat().st_size / (1024 * 1024)
        print(f"\n✅ Exportación completada!")
        print(f"📁 Archivo: {output_file}")
        print(f"📊 Tamaño: {file_size:.2f} MB")
        print(f"\n💡 Próximo paso: Configura .env para Supabase y ejecuta:")
        print(f"   python scripts/importar_datos_supabase.py --file {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    main()

