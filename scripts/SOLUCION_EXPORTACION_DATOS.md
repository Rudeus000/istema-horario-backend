# Solución para Exportar Datos a Supabase

## Problema Actual

Hay un problema de encoding en la configuración de conexión a la base de datos local que impide exportar los datos automáticamente. El error `'utf-8' codec can't decode byte 0xf3` sugiere que hay caracteres inválidos en algún parámetro de conexión (probablemente la contraseña).

## Soluciones Alternativas

### Opción 1: Usar pgAdmin o DBeaver (Recomendado)

1. **Conecta a tu base de datos local** usando pgAdmin o DBeaver
2. **Exporta cada tabla** usando la función de exportación del cliente
3. **Genera INSERTs SQL** desde el cliente
4. **Ejecuta en Supabase SQL Editor**

### Opción 2: Usar pg_dump (Si lo instalas)

Si instalas PostgreSQL client tools (que incluye `pg_dump`):

```bash
# Exportar solo datos (sin estructura)
pg_dump -h localhost -p 5434 -U postgres -d Sistemaponti \
  --data-only --column-inserts \
  --exclude-table=scheduling_horariosasignados \
  > datos_exportados.sql
```

Luego ejecuta el SQL en Supabase.

### Opción 3: Script SQL Manual

Puedes crear manualmente un script SQL consultando cada tabla. Aquí tienes un template:

```sql
-- Script para insertar datos en Supabase
-- IMPORTANTE: Ejecutar en Supabase SQL Editor

SET client_encoding TO 'UTF8';

-- 1. auth_user
-- INSERT INTO auth_user (id, username, email, ...) VALUES (...);

-- 2. academic_setup_tipounidadacademica
-- INSERT INTO academic_setup_tipounidadacademica (tipo_unidad_id, nombre_tipo, ...) VALUES (...);

-- ... (continúa con todas las tablas)
```

### Opción 4: Exportar desde Django Admin

1. Ve a Django Admin (`http://localhost:8000/admin`)
2. Exporta cada modelo manualmente usando la interfaz
3. Importa en Supabase usando `loaddata`

### Opción 5: Corregir Encoding de la Contraseña

Si la contraseña tiene caracteres especiales:

1. **Cambia la contraseña de PostgreSQL** a una sin caracteres especiales
2. O **codifica la contraseña correctamente** en el archivo `.env`

## Orden de Inserción (Importante)

Debes insertar los datos en este orden para respetar las claves foráneas:

1. `auth_user`
2. `academic_setup_tipounidadacademica`
3. `academic_setup_unidadacademica`
4. `academic_setup_tiposespacio`
5. `academic_setup_especialidades`
6. `academic_setup_carrera`
7. `academic_setup_ciclo`
8. `academic_setup_seccion`
9. `academic_setup_periodoacademico`
10. `academic_setup_materias`
11. `academic_setup_espaciosfisicos`
12. `users_roles`
13. `users_docentes`
14. `academic_setup_carreramaterias`
15. `academic_setup_materiaespecialidadesrequeridas`
16. `users_docenteespecialidades`
17. `scheduling_bloqueshorariosdefinicion`
18. `scheduling_grupos`
19. `scheduling_grupos_materias` (tabla many-to-many)
20. `scheduling_disponibilidaddocentes`
21. `scheduling_configuracionrestricciones`
22. `users_sesionesusuario`

**NOTA:** `scheduling_horariosasignados` NO debe incluirse según tu solicitud.

## Verificación

Después de insertar los datos, verifica con:

```sql
-- Contar registros por tabla
SELECT 'auth_user' as tabla, COUNT(*) as registros FROM auth_user
UNION ALL
SELECT 'academic_setup_tipounidadacademica', COUNT(*) FROM academic_setup_tipounidadacademica
-- ... (continúa con todas las tablas)
```

## Recomendación

**La forma más fácil es usar pgAdmin o DBeaver** para exportar los datos y luego ejecutarlos en Supabase SQL Editor.

