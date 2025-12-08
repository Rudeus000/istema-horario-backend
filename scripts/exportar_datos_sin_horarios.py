#!/usr/bin/env python
"""
Script para exportar datos de la base de datos LOCAL EXCLUYENDO HorariosAsignados.

Este script exporta todos los datos excepto los horarios asignados.
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
    print("  EXPORTANDO DATOS (SIN HORARIOS ASIGNADOS)")
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
    
    print("\n⚠️  IMPORTANTE: Se EXCLUIRÁ la tabla 'HorariosAsignados' de la exportación")
    print("   Se exportarán: carreras, materias, docentes, disponibilidades, grupos, etc.\n")
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"backup_sin_horarios_{timestamp}.json"
    
    print(f"📦 Exportando a: {output_file}")
    print("⏳ Esto puede tardar varios minutos...\n")
    
    try:
        call_command(
            'dumpdata',
            '--natural-foreign',
            '--natural-primary',
            '--indent', '2',
            '--output', output_file,
            '--exclude', 'scheduling.HorariosAsignados',
            verbosity=2
        )
        
        # Verificar tamaño
        file_size = Path(output_file).stat().st_size / (1024 * 1024)
        print(f"\n✅ Exportación completada!")
        print(f"📁 Archivo: {output_file}")
        print(f"📊 Tamaño: {file_size:.2f} MB")
        print(f"\n⚠️  NOTA: HorariosAsignados NO fue incluido en el backup")
        print(f"\n💡 Próximo paso: Configura .env para Supabase y ejecuta:")
        print(f"   python scripts/importar_datos_supabase.py --file {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    main()

