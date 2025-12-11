# Guía de Migración de Datos usando Django

## 📋 Pasos para Migrar Datos a Supabase

### 1. Verificar Configuración de Supabase

Asegúrate de que tu archivo `.env` esté configurado para Supabase:

```bash
# Ejecuta el script para cambiar a Supabase
python scripts/cambiar_a_supabase.ps1

# O verifica manualmente que .env tenga:
DB_HOST=dhnbtnfpqhdtbzopfguw.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=$HunterxHunter$
```

### 2. Ejecutar el Script de Migración

```bash
# Desde el directorio del backend
cd istema-horario-backend

# Activa tu entorno virtual (si usas uno)
# venv\Scripts\activate  # Windows

# Ejecuta el script de migración
python scripts/migrar_datos_django.py
```

### 3. ¿Qué hace el script?

- ✅ Se conecta a tu base de datos local
- ✅ Lee todos los datos usando Django ORM
- ✅ Limpia problemas de encoding automáticamente
- ✅ Inserta los datos en Supabase en lotes (100 registros por vez)
- ✅ Excluye `scheduling_horariosasignados` (según tu solicitud)
- ✅ Muestra progreso en tiempo real

### 4. Ventajas de este método

- ✅ **Más rápido**: Inserta en lotes
- ✅ **Más seguro**: Usa transacciones de Django
- ✅ **Maneja encoding**: Limpia problemas automáticamente
- ✅ **Sin límites de tamaño**: No hay límite del SQL Editor
- ✅ **Usa Django ORM**: Respeta las validaciones y relaciones

### 5. Verificación

Después de la migración, verifica en Supabase:

```sql
-- Verificar cantidad de registros
SELECT 
    'auth_user' as tabla, COUNT(*) as registros FROM auth_user
UNION ALL
SELECT 'academic_setup_carrera', COUNT(*) FROM academic_setup_carrera
UNION ALL
SELECT 'users_docentes', COUNT(*) FROM users_docentes
-- etc...
```

## ⚠️ Notas Importantes

1. **Orden de ejecución**: El script respeta el orden de las foreign keys
2. **Datos existentes**: El script elimina datos existentes antes de insertar (para evitar duplicados)
3. **HorariosAsignados**: NO se migra (según tu solicitud)
4. **Encoding**: Se limpia automáticamente durante la migración

## 🆘 Si hay errores

- Verifica que estés conectado a Supabase (no a local)
- Verifica que las tablas existan en Supabase (ejecuta `create_supabase_database.sql` primero)
- Revisa los mensajes de error en la consola


