# Estado de la Migración de Datos a Supabase

## ✅ Datos COMPLETOS que ya tenemos:

1. ✅ **auth_user** - 121 usuarios (COMPLETO)
2. ✅ **academic_setup_tipounidadacademica** - 2 registros (INFERIDO: Escuela, Instituto)
3. ✅ **academic_setup_unidadacademica** - 2 registros (COMPLETO)
4. ✅ **academic_setup_tiposespacio** - 4 registros (COMPLETO)
5. ✅ **academic_setup_especialidades** - 16 registros (COMPLETO)
6. ✅ **academic_setup_carrera** - 6 registros (COMPLETO)
7. ✅ **academic_setup_ciclo** - 48 registros (COMPLETO)
8. ✅ **academic_setup_periodoacademico** - 3 registros (COMPLETO)
9. ✅ **academic_setup_materias** - 144 registros (COMPLETO)
10. ✅ **users_docentes** - 117 registros (COMPLETO)
11. ✅ **academic_setup_materiaespecialidadesrequeridas** - 141 registros (COMPLETO)

## ⚠️ Datos INCOMPLETOS:

1. ⚠️ **scheduling_bloqueshorariosdefinicion** - Se cortó en la salida (necesitamos los 138 registros completos)

## ❌ Datos FALTANTES (necesitas ejecutar estas consultas):

Ejecuta estas consultas en PostgreSQL y comparte los resultados:

```sql
-- 1. Tipo de Unidad Académica (verificar que sean 2)
SELECT * FROM academic_setup_tipounidadacademica ORDER BY tipo_unidad_id;

-- 2. Secciones
SELECT * FROM academic_setup_seccion ORDER BY seccion_id;

-- 3. Espacios Físicos (si no están en el script actual)
SELECT * FROM academic_setup_espaciosfisicos ORDER BY espacio_id;

-- 4. Roles
SELECT * FROM users_roles ORDER BY rol_id;

-- 5. Carrera-Materias (relación)
SELECT * FROM academic_setup_carreramaterias;

-- 6. Docente-Especialidades (relación)
SELECT * FROM users_docenteespecialidades;

-- 7. Grupos
SELECT * FROM scheduling_grupos ORDER BY grupo_id;

-- 8. Disponibilidad Docentes
SELECT * FROM scheduling_disponibilidaddocentes ORDER BY disponibilidad_id;

-- 9. Bloques Horarios (COMPLETO - se cortó en la salida anterior)
SELECT * FROM scheduling_bloqueshorariosdefinicion ORDER BY bloque_def_id;

-- 10. Grupos-Materias (relación - verificar que sean 162)
SELECT * FROM scheduling_grupos_materias;
```

## 📝 Próximos Pasos:

1. **Ejecuta las consultas faltantes** en PostgreSQL
2. **Comparte los resultados** aquí
3. **Generaré el SQL completo** con todos los INSERTs
4. **Ejecuta el script final** en Supabase SQL Editor

## 🔍 Nota sobre Encoding:

Si ves caracteres raros como `├í`, `├▒`, etc., no te preocupes. Los limpiaré automáticamente al generar el SQL final.

## ⚠️ IMPORTANTE:

- **NO incluir** `scheduling_horariosasignados` (según tu solicitud)
- Asegúrate de copiar **TODA** la salida de cada consulta
- Si una consulta es muy larga, puedes exportarla como CSV desde pgAdmin

