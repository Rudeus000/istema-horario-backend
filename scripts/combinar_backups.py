#!/usr/bin/env python
"""
Script para combinar múltiples archivos JSON de backup en uno solo.
Útil después de exportar por apps individuales.
"""

import json
from pathlib import Path
import sys

def main():
    backup_dir = Path("backups_por_app")
    
    if not backup_dir.exists():
        print("❌ Directorio 'backups_por_app' no encontrado")
        print("   Ejecuta primero: python scripts/exportar_por_apps.py")
        return
    
    print("\n" + "=" * 60)
    print("  COMBINAR BACKUPS POR APPS")
    print("=" * 60 + "\n")
    
    # Archivos a combinar (en orden correcto)
    files_to_combine = [
        'contenttypes.json',
        'auth.json',
        'admin.json',
        'sessions.json',
        'academic_setup.json',
        'users.json',
        'scheduling.json',  # Ya sin HorariosAsignados
    ]
    
    all_data = []
    
    for filename in files_to_combine:
        filepath = backup_dir / filename
        if not filepath.exists():
            print(f"⚠️  Archivo no encontrado: {filename}")
            continue
        
        print(f"📖 Leyendo {filename}...")
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                    print(f"   ✅ {len(data)} objetos agregados")
                else:
                    all_data.append(data)
                    print(f"   ✅ 1 objeto agregado")
        except Exception as e:
            print(f"   ❌ Error leyendo {filename}: {e}")
    
    # Escribir archivo combinado
    output_file = "backup_combinado_sin_horarios.json"
    print(f"\n💾 Escribiendo archivo combinado: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    file_size = Path(output_file).stat().st_size / (1024 * 1024)
    print(f"\n✅ Archivo combinado creado!")
    print(f"📁 Archivo: {output_file}")
    print(f"📊 Tamaño: {file_size:.2f} MB")
    print(f"📦 Total de objetos: {len(all_data)}")
    print(f"\n💡 Próximo paso: Importar a Supabase")
    print(f"   python scripts/importar_datos_supabase.py --file {output_file}")

if __name__ == '__main__':
    main()

