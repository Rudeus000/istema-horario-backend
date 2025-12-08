# ✅ Verificar Conexión a Supabase

## 🔧 Configuración Completada

El archivo `.env` ha sido configurado con las credenciales de Supabase:

```env
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=$HunterxHunter$
DB_HOST=db.dhnbtnfpqhdtbzopfguw.supabase.co
DB_PORT=5432
```

## 🧪 Probar la Conexión

### Opción 1: Usando Django (Recomendado)

```bash
# Activar entorno virtual
venv\Scripts\activate

# Verificar configuración
python manage.py check --database default

# Probar conexión directa
python manage.py dbshell
```

Si conecta correctamente, verás el prompt de PostgreSQL. Escribe `\q` para salir.

### Opción 2: Usando psql (si lo tienes instalado)

```bash
psql -h db.dhnbtnfpqhdtbzopfguw.supabase.co -U postgres -d postgres -p 5432
```

Cuando te pida el password, ingresa: `$HunterxHunter$`

## 🚀 Ejecutar Migraciones

Una vez que la conexión funcione:

```bash
# Ver qué se va a crear
python manage.py migrate --plan

# Crear todas las tablas en Supabase
python manage.py migrate

# Verificar que todo esté bien
python manage.py check
```

## ⚠️ Si hay Errores

### Error: "ModuleNotFoundError: No module named 'decouple'"

Activa el entorno virtual primero:
```bash
venv\Scripts\activate
```

### Error: "could not connect to server"

1. Verifica que el password sea correcto: `$HunterxHunter$`
2. Verifica que el host sea: `db.dhnbtnfpqhdtbzopfguw.supabase.co`
3. Verifica que el puerto sea: `5432`
4. Verifica tu conexión a internet

### Error: "SSL connection required"

El `settings.py` ya está configurado para usar SSL automáticamente cuando detecta `supabase.co`. Si aún hay problemas, verifica que la línea 109 de `settings.py` tenga:

```python
'sslmode': 'require' if 'supabase.co' in config('DB_HOST', default='') else 'prefer',
```

## 📋 Checklist

- [ ] Archivo `.env` creado con las credenciales correctas
- [ ] Entorno virtual activado
- [ ] Conexión a Supabase verificada (`python manage.py dbshell`)
- [ ] Migraciones ejecutadas (`python manage.py migrate`)
- [ ] Sistema funcionando correctamente

---

**Última actualización**: 7 de Diciembre, 2025

