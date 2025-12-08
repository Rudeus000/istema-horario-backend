# 🔧 Exportar Datos Usando pg_dump (Alternativa)

Si `dumpdata` de Django falla por problemas de encoding, puedes usar `pg_dump` directamente.

## 📋 Requisitos

- PostgreSQL instalado localmente
- `pg_dump` en el PATH

## 🚀 Pasos

### 1. Exportar solo datos (sin estructura)

```powershell
# Exportar solo datos en formato SQL
pg_dump -h localhost -p 5434 -U postgres -d Sistemaponti --data-only --column-inserts > backup_datos.sql

# O exportar en formato custom (más eficiente)
pg_dump -h localhost -p 5434 -U postgres -d Sistemaponti --data-only --format=custom -f backup_datos.backup
```

### 2. Excluir HorariosAsignados

Si usas SQL, puedes editar el archivo y eliminar las líneas de `INSERT` para `horariosasignados`.

O usar un script para filtrar:

```powershell
# Filtrar solo las tablas que necesitas
pg_dump -h localhost -p 5434 -U postgres -d Sistemaponti --data-only --table=academic_setup_carrera --table=academic_setup_materias ... > backup_filtrado.sql
```

### 3. Importar a Supabase

```powershell
# Con archivo SQL
psql -h db.dhnbtnfpqhdtbzopfguw.supabase.co -p 5432 -U postgres -d postgres -f backup_datos.sql

# Con archivo custom
pg_restore -h db.dhnbtnfpqhdtbzopfguw.supabase.co -p 5432 -U postgres -d postgres backup_datos.backup
```

## ⚠️ Notas

- `pg_dump` maneja mejor el encoding que Django `dumpdata`
- El formato custom es más eficiente para bases de datos grandes
- Necesitarás el password de la base de datos cuando te lo pida

---

**Última actualización**: 7 de Diciembre, 2025

