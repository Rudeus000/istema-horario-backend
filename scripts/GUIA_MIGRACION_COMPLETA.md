# 🚀 Guía Completa de Migración a Supabase

Esta guía te explica paso a paso cómo migrar tu base de datos local a Supabase.

## 📋 Resumen del Proceso

**Opción Recomendada**: Usar migraciones de Django directamente
- Django crea todas las tablas automáticamente en Supabase
- Más seguro y confiable
- Mantiene consistencia con el código

**Opción Alternativa**: Script SQL manual + migraciones
- Útil si quieres control total sobre la creación
- Requiere ejecutar el script SQL primero

---

## 🎯 Opción 1: Migración con Django (RECOMENDADA)

### Paso 1: Crear Proyecto en Supabase

1. Ir a [supabase.com](https://supabase.com)
2. Crear cuenta o iniciar sesión
3. Crear nuevo proyecto
4. Esperar a que el proyecto se inicialice (2-3 minutos)
5. Ir a **Settings** → **Database** y copiar:
   - **Connection string** (URI)
   - **Database password**

### Paso 2: Configurar Variables de Entorno

Editar el archivo `.env` en la raíz del backend:

```env
# Supabase Database
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=tu_password_de_supabase
DB_HOST=db.tu-proyecto-id.supabase.co
DB_PORT=5432
```

**Obtener estos valores desde Supabase:**
- **DB_HOST**: En Settings → Database → Connection string, buscar `@db.xxxxx.supabase.co`
- **DB_PASSWORD**: La contraseña que configuraste al crear el proyecto
- **DB_NAME**: Siempre es `postgres` en Supabase
- **DB_USER**: Siempre es `postgres` en Supabase

### Paso 3: Verificar Configuración de Django

Asegúrate de que `settings.py` tenga SSL configurado:

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
            'sslmode': 'require',  # ⚠️ IMPORTANTE: Supabase requiere SSL
        },
    }
}
```

### Paso 4: Probar Conexión

```bash
# Activar entorno virtual
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Probar conexión
python manage.py dbshell
```

Si conecta correctamente, verás el prompt de PostgreSQL. Escribe `\q` para salir.

### Paso 5: Ejecutar Migraciones

**⚠️ IMPORTANTE**: Esto creará TODAS las tablas directamente en Supabase.

```bash
# 1. Ver qué migraciones se van a aplicar
python manage.py migrate --plan

# 2. Aplicar todas las migraciones
python manage.py migrate

# 3. Verificar que no haya errores
python manage.py check
```

**¿Qué hace `migrate`?**
- Crea todas las tablas en Supabase
- Crea todas las relaciones (Foreign Keys)
- Crea todos los índices
- Crea todos los constraints
- Registra las migraciones en `django_migrations`

### Paso 6: Verificar en Supabase

1. Ir a Supabase Dashboard → **Table Editor**
2. Deberías ver todas las tablas creadas:
   - `academic_setup_*` (12 tablas)
   - `users_*` (4 tablas)
   - `scheduling_*` (6 tablas)
   - `auth_*` (tablas de Django)
   - `django_*` (tablas de Django)

### Paso 7: Crear Superusuario (Opcional)

```bash
python manage.py createsuperuser
```

Esto creará el usuario directamente en Supabase.

---

## 🔧 Opción 2: Script SQL Manual + Migraciones

Si prefieres crear la estructura manualmente primero:

### Paso 1-3: Igual que la Opción 1

### Paso 4: Ejecutar Script SQL

1. Ir a Supabase Dashboard → **SQL Editor**
2. Crear nueva query
3. Abrir el archivo `scripts/create_supabase_database.sql`
4. Copiar y pegar todo el contenido
5. Ejecutar el script
6. Verificar que no haya errores

### Paso 5: Ejecutar Migraciones de Django

```bash
# Django detectará que las tablas ya existen
# Solo aplicará migraciones faltantes o nuevas
python manage.py migrate
```

**Ventaja**: Tienes control total sobre la creación inicial
**Desventaja**: Puede haber inconsistencias si el script SQL no coincide exactamente con Django

---

## 📊 ¿Qué Tablas Crea Django?

Cuando ejecutas `python manage.py migrate`, Django crea:

### Tablas de Django (automáticas):
- `auth_user` - Usuarios
- `auth_group` - Grupos
- `auth_permission` - Permisos
- `auth_user_groups` - Usuarios ↔ Grupos
- `auth_user_user_permissions` - Usuarios ↔ Permisos
- `auth_group_permissions` - Grupos ↔ Permisos
- `django_content_type` - Metadatos de modelos
- `django_migrations` - Historial de migraciones
- `django_session` - Sesiones
- `django_admin_log` - Logs del admin

### Tablas de tu Aplicación:
- `academic_setup_*` (12 tablas)
- `users_*` (4 tablas)
- `scheduling_*` (6 tablas)

**Total**: ~30+ tablas

---

## ✅ Verificación Post-Migración

### 1. Verificar Tablas Creadas

En Supabase SQL Editor:

```sql
SELECT COUNT(*) as total_tablas
FROM information_schema.tables 
WHERE table_schema = 'public';
```

**Resultado esperado**: ~30+ tablas

### 2. Verificar desde Django

```bash
python manage.py shell
```

```python
# Probar consultas
from apps.academic_setup.models import Carrera, UnidadAcademica
from apps.users.models import Docentes
from apps.scheduling.models import Grupos

# Deberían funcionar sin errores
print(f"Unidades: {UnidadAcademica.objects.count()}")
print(f"Carreras: {Carrera.objects.count()}")
print(f"Docentes: {Docentes.objects.count()}")
```

### 3. Verificar Foreign Keys

```sql
SELECT COUNT(*) 
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
AND table_schema = 'public';
```

**Resultado esperado**: ~25-30 Foreign Keys

---

## 🔄 Migrar Datos Existentes

Si ya tienes datos en tu base de datos local:

### Opción A: Exportar/Importar con pg_dump

```bash
# 1. Exportar datos de la BD local (solo datos, sin estructura)
pg_dump -h localhost -U postgres -d Sistemaponti \
  --data-only \
  --inserts \
  --exclude-table=django_migrations \
  > datos_local.sql

# 2. Importar a Supabase
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres" \
  -f datos_local.sql
```

### Opción B: Usar Django Management Commands

```bash
# Exportar datos
python manage.py dumpdata > datos_backup.json

# Cambiar configuración a Supabase
# (actualizar .env)

# Importar datos
python manage.py loaddata datos_backup.json
```

---

## 🐛 Solución de Problemas

### Error: "SSL connection required"

**Solución**: Asegúrate de tener `'sslmode': 'require'` en `settings.py`

### Error: "relation already exists"

**Solución**: Django detecta tablas existentes y las omite. No es un error.

### Error: "password authentication failed"

**Solución**: Verifica las credenciales en `.env`

### Error: "could not connect to server"

**Solución**: 
- Verifica que el proyecto de Supabase esté activo
- Verifica el `DB_HOST` en `.env`
- Verifica que no haya firewall bloqueando la conexión

### Las migraciones no se aplican

**Solución**:
```bash
# Ver estado de migraciones
python manage.py showmigrations

# Forzar migración específica
python manage.py migrate app_name migration_name --fake
```

---

## 📝 Checklist de Migración

- [ ] Proyecto creado en Supabase
- [ ] Credenciales copiadas y guardadas
- [ ] `.env` actualizado con credenciales de Supabase
- [ ] `settings.py` configurado con SSL
- [ ] Conexión probada con `python manage.py dbshell`
- [ ] Migraciones ejecutadas: `python manage.py migrate`
- [ ] Tablas verificadas en Supabase Dashboard
- [ ] Consultas de prueba funcionando
- [ ] Superusuario creado (opcional)
- [ ] Datos migrados (si aplica)

---

## 🎉 ¡Listo!

Una vez completados estos pasos, tu aplicación Django estará usando Supabase como base de datos. Todas las operaciones (crear, leer, actualizar, eliminar) se realizarán directamente en Supabase.

---

**Última actualización**: 7 de Diciembre, 2025

