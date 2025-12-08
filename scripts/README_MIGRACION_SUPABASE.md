# 📋 Guía de Migración a Supabase

Esta guía explica cómo migrar la base de datos del Sistema de Horarios a Supabase.

## 📁 Archivos Incluidos

1. **`create_supabase_database.sql`** - Script principal para crear toda la estructura
2. **`verify_supabase_database.sql`** - Script de verificación post-migración

## 🚀 Pasos para Migrar

### Paso 1: Crear Proyecto en Supabase

1. Ir a [supabase.com](https://supabase.com)
2. Crear una cuenta o iniciar sesión
3. Crear un nuevo proyecto
4. Anotar las credenciales:
   - Database URL
   - API Key
   - Service Role Key

### Paso 2: Configurar Django para Supabase

**IMPORTANTE**: Antes de ejecutar migraciones, configura Django para usar Supabase.

1. Actualizar el archivo `.env` del backend:

```env
# Supabase Database
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=tu_password_de_supabase
DB_HOST=db.tu-proyecto.supabase.co
DB_PORT=5432
```

2. Verificar que `settings.py` tenga la configuración correcta:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='postgres'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default=5432),
        'OPTIONS': {
            'sslmode': 'require',  # Supabase requiere SSL
        },
    }
}
```

### Paso 3: Opciones para Crear la Estructura

Tienes **DOS OPCIONES** para crear las tablas:

#### ⚠️ OPCIÓN RECOMENDADA: Usar Migraciones de Django

**Esta es la forma más segura y recomendada** porque Django crea todas las tablas con la estructura exacta que necesita.

```bash
# 1. Verificar conexión a Supabase
python manage.py dbshell
# Si conecta correctamente, salir con \q

# 2. Ver qué migraciones se van a aplicar
python manage.py migrate --plan

# 3. Aplicar todas las migraciones (esto crea TODAS las tablas en Supabase)
python manage.py migrate

# 4. Verificar que todo esté correcto
python manage.py check
```

**¿Qué hace esto?**
- Django crea **TODAS** las tablas directamente en Supabase
- Incluye tablas de Django (auth_user, auth_group, django_migrations, etc.)
- Incluye todas tus tablas personalizadas (academic_setup_*, users_*, scheduling_*)
- Crea todas las relaciones, índices y constraints automáticamente
- Registra las migraciones en `django_migrations`

#### Opción Alternativa: Script SQL Manual

Si prefieres crear la estructura manualmente primero:

1. Ir a **SQL Editor** en el dashboard de Supabase
2. Abrir el archivo `create_supabase_database.sql`
3. Copiar y pegar todo el contenido
4. Ejecutar el script
5. Luego ejecutar `python manage.py migrate` (solo aplicará migraciones faltantes)

**Nota**: Si usas el script SQL primero, Django detectará que las tablas ya existen y solo creará las que falten.

### Paso 4: Verificar la Estructura

Después de ejecutar las migraciones, verificar que todo esté correcto:

#### Opción A: Script SQL de Verificación

Ejecutar el script de verificación en Supabase SQL Editor:

```sql
-- Copiar y pegar el contenido de verify_supabase_database.sql
```

#### Opción B: Desde Django

```bash
# Verificar conexión y estructura
python manage.py dbshell

# Dentro de psql, verificar tablas:
\dt

# Ver todas las tablas creadas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

### Paso 5: Migrar Datos (Opcional)

Si ya tienes datos en la base de datos local:

```bash
# Exportar datos locales
pg_dump -h localhost -U postgres -d Sistemaponti --data-only --inserts > datos_local.sql

# Importar a Supabase
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres" < datos_local.sql
```

### Paso 6: Verificar que Todo Funciona

```bash
# Verificar que Django puede conectarse
python manage.py check --database default

# Probar una consulta simple
python manage.py shell
# >>> from apps.academic_setup.models import Carrera
# >>> Carrera.objects.count()
# Debería funcionar sin errores
```

## ✅ Verificaciones Post-Migración

### 1. Verificar Tablas Creadas

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND (table_name LIKE 'academic_setup_%' 
     OR table_name LIKE 'users_%' 
     OR table_name LIKE 'scheduling_%')
ORDER BY table_name;
```

**Resultado esperado**: 22 tablas

### 2. Verificar Foreign Keys

```sql
SELECT COUNT(*) 
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
AND table_schema = 'public';
```

**Resultado esperado**: ~25 Foreign Keys

### 3. Verificar Constraints UNIQUE

```sql
SELECT COUNT(*) 
FROM information_schema.table_constraints
WHERE constraint_type = 'UNIQUE'
AND table_schema = 'public';
```

**Resultado esperado**: ~15 Constraints UNIQUE

### 4. Probar Conexión desde Django

```python
# En Django shell
python manage.py shell

from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) FROM academic_setup_carrera")
print(cursor.fetchone())
```

## 🔧 Solución de Problemas

### Error: "relation already exists"

Si una tabla ya existe, el script usa `CREATE TABLE IF NOT EXISTS`, pero si necesitas recrear:

```sql
DROP TABLE IF EXISTS nombre_tabla CASCADE;
```

### Error: "permission denied"

Asegúrate de usar el usuario `postgres` o un usuario con permisos suficientes.

### Error: "SSL connection required"

Supabase requiere SSL. Asegúrate de tener `'sslmode': 'require'` en la configuración.

### Error: "constraint does not exist"

Verifica que todas las tablas referenciadas existan antes de crear Foreign Keys.

## 📊 Estructura Esperada

### Tablas Academic Setup (12)
- academic_setup_tipounidadacademica
- academic_setup_unidadacademica
- academic_setup_carrera
- academic_setup_ciclo
- academic_setup_seccion
- academic_setup_periodoacademico
- academic_setup_tiposespacio
- academic_setup_espaciosfisicos
- academic_setup_especialidades
- academic_setup_materias
- academic_setup_carreramaterias
- academic_setup_materiaespecialidadesrequeridas

### Tablas Users (4)
- users_roles
- users_docentes
- users_docenteespecialidades
- users_sesionesusuario

### Tablas Scheduling (5)
- scheduling_bloqueshorariosdefinicion
- scheduling_grupos
- scheduling_grupos_materias
- scheduling_disponibilidaddocentes
- scheduling_horariosasignados
- scheduling_configuracionrestricciones

**Total**: 22 tablas principales

## 🔐 Seguridad

- ⚠️ **NUNCA** subas el archivo `.env` con credenciales a Git
- ⚠️ Usa variables de entorno en producción
- ⚠️ Limita el acceso a la base de datos en Supabase
- ⚠️ Usa Row Level Security (RLS) si es necesario

## 📝 Notas Importantes

1. **Timezone**: El script configura `America/Lima` como timezone
2. **Encoding**: UTF-8 para soportar caracteres especiales
3. **Sequences**: Se crean automáticamente con `SERIAL`
4. **Índices**: Se crean índices en campos frecuentemente consultados

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs de Supabase
2. Ejecuta el script de verificación
3. Compara la estructura con la base de datos local
4. Verifica las credenciales de conexión

---

**Última actualización**: 7 de Diciembre, 2025


