# 📦 Guía: Migrar Datos de Base de Datos Local a Supabase

## 🎯 Objetivo

Migrar todos los datos de tu base de datos local (PostgreSQL) a Supabase.

## 📋 Opciones de Migración

### Opción 1: Usando Django `dumpdata` y `loaddata` (Recomendado) ⭐

Esta es la forma más segura y compatible con Django.

#### Paso 1: Exportar datos de la base de datos local

```bash
# Activar entorno virtual
cd istema-horario-backend
.\venv\Scripts\activate

# Configurar .env para usar base de datos LOCAL
# Editar .env temporalmente:
# DB_HOST=localhost
# DB_PORT=5434  (o el puerto que uses)
# DB_NAME=Sistemaponti
# DB_USER=postgres
# DB_PASSWORD=tu_password_local

# Exportar todos los datos (EXCLUYENDO HorariosAsignados)
python manage.py dumpdata --natural-foreign --natural-primary --exclude scheduling.HorariosAsignados -o datos_local.json

# O exportar por app específica:
python manage.py dumpdata academic_setup -o academic_setup.json
python manage.py dumpdata users -o users.json
python manage.py dumpdata scheduling --exclude scheduling.HorariosAsignados -o scheduling.json
```

#### Paso 2: Cambiar configuración a Supabase

```bash
# Editar .env para usar Supabase:
# DB_HOST=db.dhnbtnfpqhdtbzopfguw.supabase.co
# DB_PORT=5432
# DB_NAME=postgres
# DB_USER=postgres
# DB_PASSWORD=$HunterxHunter$
```

#### Paso 3: Importar datos a Supabase

```bash
# Importar todos los datos
python manage.py loaddata datos_local.json

# O importar por app:
python manage.py loaddata academic_setup.json
python manage.py loaddata users.json
python manage.py loaddata scheduling.json
```

### Opción 2: Usando pg_dump y psql (PostgreSQL nativo)

Requiere tener PostgreSQL instalado localmente.

#### Paso 1: Exportar desde base de datos local

```bash
# Exportar solo datos (sin estructura)
pg_dump -h localhost -p 5434 -U postgres -d Sistemaponti --data-only --column-inserts > datos_local.sql

# O exportar todo (estructura + datos)
pg_dump -h localhost -p 5434 -U postgres -d Sistemaponti > backup_completo.sql
```

#### Paso 2: Importar a Supabase

```bash
# Importar solo datos
psql -h db.dhnbtnfpqhdtbzopfguw.supabase.co -p 5432 -U postgres -d postgres -f datos_local.sql

# Cuando pida password, ingresar: $HunterxHunter$
```

### Opción 3: Script Python personalizado

Ver `migrar_datos.py` para un script automatizado.

## ⚠️ Consideraciones Importantes

### 1. Orden de Importación

Debido a las Foreign Keys, importa en este orden:

1. **auth** (usuarios del sistema)
2. **academic_setup** (carreras, materias, etc.)
3. **users** (docentes, roles)
4. **scheduling** (disponibilidades, grupos, etc.)
   - ⚠️ **NOTA**: `HorariosAsignados` NO se migra (excluido intencionalmente)

### 2. Conflictos de IDs

Si hay conflictos con IDs existentes, puedes:

```bash
# Limpiar datos existentes en Supabase (CUIDADO!)
python manage.py flush --noinput

# O importar ignorando conflictos
python manage.py loaddata datos_local.json --verbosity 2
```

### 3. Foreign Keys y Dependencias

Django `dumpdata` con `--natural-foreign` y `--natural-primary` maneja automáticamente las dependencias.

### 4. Datos Sensibles

- **Usuarios**: Se migrarán con sus passwords hasheados
- **Tokens JWT**: Pueden necesitar regenerarse
- **Sesiones**: Probablemente quieras limpiarlas

## 🔧 Scripts Disponibles

- `migrar_datos.py` - Script automatizado de migración
- `exportar_datos_local.py` - Solo exportar
- `importar_datos_supabase.py` - Solo importar

## 📝 Ejemplo Completo

```bash
# 1. Activar entorno virtual
cd istema-horario-backend
.\venv\Scripts\activate

# 2. Configurar .env para LOCAL
# Editar .env: DB_HOST=localhost, DB_PORT=5434

# 3. Exportar datos (EXCLUYENDO HorariosAsignados)
python manage.py dumpdata --natural-foreign --natural-primary --exclude scheduling.HorariosAsignados -o backup_completo.json

# 4. Configurar .env para SUPABASE
# Editar .env: DB_HOST=db.dhnbtnfpqhdtbzopfguw.supabase.co, DB_PORT=5432

# 5. Importar datos
python manage.py loaddata backup_completo.json

# 6. Verificar
python manage.py shell
>>> from academic_setup.models import Carrera
>>> Carrera.objects.count()  # Debería mostrar tus carreras
```

## 🚨 Troubleshooting

### Error: "duplicate key value violates unique constraint"

Las tablas ya tienen datos. Opciones:

1. **Limpiar primero** (CUIDADO: borra todo):
   ```bash
   python manage.py flush --noinput
   python manage.py loaddata backup_completo.json
   ```

2. **Ignorar errores** (puede dejar datos inconsistentes):
   ```bash
   python manage.py loaddata backup_completo.json --verbosity 2
   ```

### Error: "relation does not exist"

Las tablas no existen. Ejecuta:
```bash
python manage.py migrate
```

### Error: "foreign key constraint"

Importa en el orden correcto (ver sección "Orden de Importación").

---

**Última actualización**: 7 de Diciembre, 2025

