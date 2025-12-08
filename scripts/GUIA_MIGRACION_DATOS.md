# 📦 Guía Rápida: Migrar Datos de Local a Supabase

## 🎯 Pasos para Migrar Datos (Sin HorariosAsignados)

### Paso 1: Cambiar a Base de Datos LOCAL

```powershell
cd istema-horario-backend
.\scripts\cambiar_a_local.ps1
```

**Nota**: Si es la primera vez, te pedirá el password de tu base de datos local.

### Paso 2: Exportar Datos (Sin HorariosAsignados)

```powershell
.\venv\Scripts\activate
python scripts/exportar_datos_sin_horarios.py
```

Esto creará un archivo `backup_sin_horarios_YYYYMMDD_HHMMSS.json`

### Paso 3: Cambiar a Supabase

```powershell
.\scripts\cambiar_a_supabase.ps1
```

### Paso 4: Importar Datos a Supabase

```powershell
python scripts/importar_datos_supabase.py --file backup_sin_horarios_YYYYMMDD_HHMMSS.json
```

Si quieres limpiar los datos existentes en Supabase primero:
```powershell
python scripts/importar_datos_supabase.py --file backup_sin_horarios_YYYYMMDD_HHMMSS.json --flush
```

## 📋 Resumen de Scripts

| Script | Propósito |
|--------|-----------|
| `cambiar_a_local.ps1` | Cambiar .env a base de datos local |
| `cambiar_a_supabase.ps1` | Cambiar .env a Supabase |
| `exportar_datos_sin_horarios.py` | Exportar datos (sin HorariosAsignados) |
| `importar_datos_supabase.py` | Importar datos a Supabase |

## ⚠️ Importante

- **HorariosAsignados NO se migrará** (excluido intencionalmente)
- Asegúrate de tener el password de tu base de datos local
- El archivo de backup es importante, guárdalo por si acaso

## 🔍 Verificar Después de Migrar

```powershell
python manage.py shell
```

```python
from academic_setup.models import Carrera
from users.models import Docentes
from scheduling.models import HorariosAsignados

print(f"Carreras: {Carrera.objects.count()}")
print(f"Docentes: {Docentes.objects.count()}")
print(f"Horarios: {HorariosAsignados.objects.count()}")  # Debería ser 0
```

---

**Última actualización**: 7 de Diciembre, 2025

