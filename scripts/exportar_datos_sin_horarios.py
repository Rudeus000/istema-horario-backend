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
from django.db import connection
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
        # Usar subprocess para ejecutar dumpdata y capturar bytes directamente
        # Esto evita problemas de encoding en la serialización de Django
        import subprocess
        import os
        
        print("📝 Ejecutando dumpdata con manejo de encoding...")
        
        # Ejecutar el comando como subprocess para capturar bytes
        manage_py = str(BASE_DIR / 'manage.py')
        result = subprocess.run(
            [sys.executable, manage_py, 'dumpdata',
             '--natural-foreign', '--natural-primary',
             '--exclude', 'scheduling.HorariosAsignados',
             '--indent', '2'],
            capture_output=True,
            text=False,  # Capturar como bytes
            cwd=str(BASE_DIR),
            env=os.environ.copy()
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='replace')
            raise Exception(f"Error en dumpdata: {error_msg}")
        
        # Decodificar con manejo de errores (reemplaza caracteres inválidos)
        print("🔧 Decodificando datos con manejo de encoding...")
        content = result.stdout.decode('utf-8', errors='replace')
        
        # Escribir el archivo con encoding UTF-8
        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            f.write(content)
        
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

