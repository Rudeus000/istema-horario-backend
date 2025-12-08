#!/usr/bin/env python
"""
Script para exportar datos limpiando caracteres con encoding problemático.
Lee los datos directamente desde PostgreSQL y los limpia antes de exportar.
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

from django.conf import settings
from django.db import connection
from django.core.serializers import serialize
from django.apps import apps

def clean_string(value):
    """Limpiar string de caracteres inválidos"""
    if value is None:
        return None
    if isinstance(value, str):
        # Reemplazar caracteres inválidos
        try:
            # Intentar codificar y decodificar para limpiar
            return value.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        except:
            return value
    return value

def clean_dict(data):
    """Limpiar diccionario recursivamente"""
    if isinstance(data, dict):
        return {k: clean_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_dict(item) for item in data]
    elif isinstance(data, str):
        return clean_string(data)
    return data

def export_model(model_class, exclude_models=None):
    """Exportar un modelo limpiando encoding"""
    if exclude_models and model_class.__name__ in exclude_models:
        return []
    
    model_name = f"{model_class._meta.app_label}.{model_class.__name__}"
    print(f"   📦 Exportando {model_name}...", end=" ")
    
    try:
        # Obtener todos los objetos
        objects = list(model_class.objects.all())
        
        # Serializar
        serialized = serialize('python', objects)
        
        # Limpiar datos
        cleaned = clean_dict(serialized)
        
        print(f"✅ {len(objects)} objetos")
        return cleaned
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    print("\n" + "=" * 60)
    print("  EXPORTAR DATOS LIMPIANDO ENCODING")
    print("=" * 60 + "\n")
    
    db_config = settings.DATABASES['default']
    print(f"📊 Base de datos: {db_config['HOST']}:{db_config['PORT']}/{db_config['NAME']}\n")
    
    # Configurar encoding en la conexión
    print("🔧 Configurando encoding...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET client_encoding TO 'UTF8'")
    except:
        pass
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"backup_sin_horarios_{timestamp}.json"
    
    print(f"📦 Exportando a: {output_file}")
    print("⏳ Esto puede tardar varios minutos...\n")
    
    all_data = []
    
    # Apps a exportar
    apps_to_export = [
        'contenttypes',
        'auth',
        'admin',
        'sessions',
        'academic_setup',
        'users',
        'scheduling',
    ]
    
    # Modelos a excluir
    exclude_models = ['HorariosAsignados']
    
    print("📋 Exportando apps...\n")
    
    for app_label in apps_to_export:
        try:
            app_config = apps.get_app_config(app_label)
            print(f"📦 App: {app_label}")
            
            for model in app_config.get_models():
                model_data = export_model(model, exclude_models)
                if model_data:
                    all_data.extend(model_data)
            
            print()
            
        except Exception as e:
            print(f"⚠️  Error en app {app_label}: {e}\n")
    
    # Escribir archivo
    print(f"💾 Escribiendo archivo: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    file_size = Path(output_file).stat().st_size / (1024 * 1024)
    print(f"\n✅ Exportación completada!")
    print(f"📁 Archivo: {output_file}")
    print(f"📊 Tamaño: {file_size:.2f} MB")
    print(f"📦 Total de objetos: {len(all_data)}")
    print(f"\n⚠️  NOTA: HorariosAsignados NO fue incluido")
    print(f"\n💡 Próximo paso: Importar a Supabase")
    print(f"   python scripts/importar_datos_supabase.py --file {output_file}")

if __name__ == '__main__':
    main()

