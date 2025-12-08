#!/usr/bin/env python
"""
Script para exportar datos por apps individuales.
Esto ayuda a identificar qué app/tabla tiene problemas de encoding.
"""

import os
import sys
import django
from pathlib import Path
import subprocess
import json
from datetime import datetime

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la_pontificia_horarios.settings')
django.setup()

from django.conf import settings

def export_app(app_name, output_dir="backups_por_app"):
    """Exportar una app específica"""
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(exist_ok=True)
    
    output_file = output_dir_path / f"{app_name}.json"
    
    print(f"\n📦 Exportando {app_name}...")
    
    try:
        manage_py = str(BASE_DIR / 'manage.py')
        result = subprocess.run(
            [sys.executable, manage_py, 'dumpdata',
             '--natural-foreign', '--natural-primary',
             '--indent', '2', app_name],
            capture_output=True,
            text=False,
            cwd=str(BASE_DIR),
            env=os.environ.copy()
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='replace')
            print(f"❌ Error en {app_name}: {error_msg[:200]}")
            return False
        
        # Decodificar con manejo de errores
        content = result.stdout.decode('utf-8', errors='replace')
        
        # Escribir archivo
        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            f.write(content)
        
        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"✅ {app_name} exportado: {file_size:.2f} MB")
        return True
        
    except Exception as e:
        print(f"❌ Error exportando {app_name}: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("  EXPORTAR DATOS POR APPS (SIN HORARIOS ASIGNADOS)")
    print("=" * 60 + "\n")
    
    db_config = settings.DATABASES['default']
    print(f"📊 Base de datos: {db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}\n")
    
    # Apps a exportar (excluyendo HorariosAsignados manualmente)
    apps = [
        'auth',
        'contenttypes',
        'admin',
        'sessions',
        'academic_setup',
        'users',
        'scheduling',  # Exportaremos pero excluiremos HorariosAsignados después
    ]
    
    print("📋 Apps a exportar:")
    for app in apps:
        print(f"   - {app}")
    print("\n⚠️  NOTA: scheduling se exportará pero HorariosAsignados se excluirá manualmente\n")
    
    input("Presiona Enter para comenzar...")
    
    success_count = 0
    failed_apps = []
    
    for app in apps:
        if app == 'scheduling':
            # Para scheduling, exportar modelos individuales excluyendo HorariosAsignados
            scheduling_models = [
                'scheduling.BloquesHorariosDefinicion',
                'scheduling.ConfiguracionRestricciones',
                'scheduling.Grupos',
                'scheduling.DisponibilidadDocentes',
            ]
            
            print(f"\n📦 Exportando scheduling (modelos individuales)...")
            output_dir = Path("backups_por_app")
            output_dir.mkdir(exist_ok=True)
            
            all_content = []
            for model in scheduling_models:
                print(f"   Exportando {model}...")
                try:
                    manage_py = str(BASE_DIR / 'manage.py')
                    result = subprocess.run(
                        [sys.executable, manage_py, 'dumpdata',
                         '--natural-foreign', '--natural-primary',
                         '--indent', '2', model],
                        capture_output=True,
                        text=False,
                        cwd=str(BASE_DIR),
                        env=os.environ.copy()
                    )
                    
                    if result.returncode == 0:
                        content = result.stdout.decode('utf-8', errors='replace')
                        # Parsear JSON y agregar a la lista
                        import json
                        try:
                            data = json.loads(content)
                            if isinstance(data, list):
                                all_content.extend(data)
                        except:
                            pass
                except Exception as e:
                    print(f"   ⚠️  Error en {model}: {e}")
            
            # Escribir archivo combinado
            output_file = output_dir / "scheduling.json"
            with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                json.dump(all_content, f, indent=2, ensure_ascii=False)
            
            file_size = output_file.stat().st_size / (1024 * 1024)
            print(f"✅ scheduling exportado: {file_size:.2f} MB (sin HorariosAsignados)")
            success_count += 1
        else:
            if export_app(app):
                success_count += 1
            else:
                failed_apps.append(app)
    
    print("\n" + "=" * 60)
    print(f"✅ Exportación completada: {success_count}/{len(apps)} apps")
    if failed_apps:
        print(f"❌ Apps con errores: {', '.join(failed_apps)}")
    print(f"📁 Archivos guardados en: backups_por_app/")
    print("\n💡 Próximo paso: Combinar archivos o importar individualmente")

if __name__ == '__main__':
    main()

