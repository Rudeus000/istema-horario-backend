# 🔌 Explicación: Conexión a Supabase

## ⚠️ IMPORTANTE: Dos Formas de Conectarse a Supabase

Supabase ofrece **DOS formas diferentes** de interactuar con la base de datos:

### 1. 🔵 API REST de Supabase (usa API Key)
- **Para qué**: Hacer peticiones HTTP desde el frontend o aplicaciones externas
- **Usa**: La API Key (anon key) que tienes
- **Ejemplo**: `fetch('https://dhnbtnfpqhdtbzopfguw.supabase.co/rest/v1/tabla')`
- **No es lo que Django usa**

### 2. 🟢 Conexión Directa a PostgreSQL (usa Password de BD)
- **Para qué**: Django se conecta directamente a PostgreSQL como si fuera una BD normal
- **Usa**: Password de la base de datos (NO la API Key)
- **Ejemplo**: Django usa `psycopg2` para conectarse directamente
- **Esto es lo que Django necesita**

## 🔑 ¿Por qué Django Necesita el Password?

Django **NO usa la API REST** de Supabase. Django se conecta **directamente a PostgreSQL** usando el driver `psycopg2`, igual que si fuera una base de datos local.

```
Django → psycopg2 → PostgreSQL (Supabase) → Base de Datos
```

**NO es:**
```
Django → API REST → Supabase → Base de Datos  ❌
```

Por eso necesitas:
- ✅ **Password de la base de datos** (para PostgreSQL)
- ❌ **NO la API Key** (esa es solo para API REST)

## 🔌 Sobre el Puerto 5432

El puerto **5432 es el puerto estándar de PostgreSQL**, tanto para:
- Bases de datos locales (localhost:5432)
- Bases de datos remotas como Supabase (db.xxxxx.supabase.co:5432)

**No es solo para local**. Supabase también usa el puerto 5432 para la conexión directa a PostgreSQL.

### Ejemplo de Conexión:

```
Local:
  Host: localhost
  Port: 5432  ← Puerto estándar de PostgreSQL

Supabase:
  Host: db.dhnbtnfpqhdtbzopfguw.supabase.co
  Port: 5432  ← Mismo puerto, pero en Supabase
```

## 📋 Resumen de Credenciales

### Para API REST (Frontend/HTTP):
```
URL: https://dhnbtnfpqhdtbzopfguw.supabase.co
API Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Para Conexión Directa PostgreSQL (Django):
```
Host: db.dhnbtnfpqhdtbzopfguw.supabase.co
Port: 5432
User: postgres
Password: [El password que configuraste al crear el proyecto]
Database: postgres
```

## 🔍 Cómo Obtener el Password de la Base de Datos

1. Ir a: https://dhnbtnfpqhdtbzopfguw.supabase.co
2. **Settings** → **Database**
3. Buscar **"Connection string"** o **"Database password"**
4. Hacer clic en **"Show password"** o **"Reveal"**
5. Copiar el password

**O si no lo recuerdas:**
- **Settings** → **Database** → **"Reset database password"**
- Configurar un nuevo password y guardarlo

## ✅ Configuración Correcta para Django

En tu archivo `.env`:

```env
# Conexión directa a PostgreSQL de Supabase
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=tu_password_de_la_bd  # ← Este es el password de BD, NO la API Key
DB_HOST=db.dhnbtnfpqhdtbzopfguw.supabase.co
DB_PORT=5432  # ← Puerto estándar de PostgreSQL (no es solo para local)
```

## 🎯 Flujo Completo

```
┌─────────────────┐
│   Django App    │
└────────┬────────┘
         │
         │ psycopg2 (driver PostgreSQL)
         │
         ▼
┌─────────────────────────────────────┐
│  PostgreSQL en Supabase             │
│  db.xxxxx.supabase.co:5432           │
│  Usuario: postgres                   │
│  Password: [tu_password_de_bd]      │
└─────────────────────────────────────┘
```

**NO es:**
```
Django → API REST → Supabase  ❌
```

## 💡 Analogía

Piensa en Supabase como un servidor PostgreSQL normal:
- **API REST** = Una capa adicional para hacer peticiones HTTP
- **PostgreSQL directo** = La base de datos real a la que Django se conecta

Django usa la conexión directa, no la API REST.

---

**Última actualización**: 7 de Diciembre, 2025

