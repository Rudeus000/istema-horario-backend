# 🔧 Configuración Rápida de Supabase

## 📍 Información del Proyecto

- **URL del Proyecto**: https://dhnbtnfpqhdtbzopfguw.supabase.co
- **Project Reference**: `dhnbtnfpqhdtbzopfguw`
- **Database Host**: `db.dhnbtnfpqhdtbzopfguw.supabase.co`
- **API Key (anon)**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRobmJ0bmZwcWhkdGJ6b3BmZ3V3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMzc2MDEsImV4cCI6MjA4MDcxMzYwMX0.Gc4iIAi7fXyvWjiRJbbhJBd7WK_hlXgH35nZHSbhIXM`

## 🔑 Obtener el Password de la Base de Datos

**IMPORTANTE**: La API Key que tienes es para usar la API REST de Supabase. Para conectarte directamente a PostgreSQL necesitas el **password de la base de datos**.

### Cómo obtener el password:

1. Ir a tu proyecto en Supabase: https://dhnbtnfpqhdtbzopfguw.supabase.co
2. Ir a **Settings** (Configuración) → **Database**
3. Buscar la sección **Connection string**
4. Seleccionar **URI** o **Connection pooling**
5. Hacer clic en **"Show password"** o **"Reveal"**
6. Copiar el password que aparece

**O si olvidaste el password:**
1. Ir a **Settings** → **Database**
2. Buscar **Database password**
3. Hacer clic en **"Reset database password"**
4. Configurar un nuevo password y guardarlo

## ⚙️ Configurar .env

Una vez que tengas el password, edita el archivo `.env` en la raíz del backend:

```env
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=TU_PASSWORD_AQUI  # ← Pegar el password aquí
DB_HOST=db.dhnbtnfpqhdtbzopfguw.supabase.co
DB_PORT=5432
```

## ✅ Verificar Conexión

```bash
# Activar entorno virtual
venv\Scripts\activate

# Probar conexión
python manage.py dbshell
```

Si conecta correctamente, verás el prompt de PostgreSQL. Escribe `\q` para salir.

## 🚀 Ejecutar Migraciones

Una vez que la conexión funcione:

```bash
# Ver qué se va a crear
python manage.py migrate --plan

# Crear todas las tablas en Supabase
python manage.py migrate

# Verificar
python manage.py check
```

## 📝 Notas

- El archivo `.env` ya está configurado con el host correcto
- Solo necesitas agregar el password de la base de datos
- El `settings.py` ya está configurado para usar SSL automáticamente cuando detecta `supabase.co` en el host

---

**Última actualización**: 7 de Diciembre, 2025

