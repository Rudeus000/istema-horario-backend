# Consultas Faltantes para Completar la Migración

## ✅ Datos que YA tienes:
1. ✅ auth_user (121 usuarios)
2. ✅ academic_setup_unidadacademica (2 registros)
3. ✅ academic_setup_tiposespacio (4 registros)
4. ✅ academic_setup_especialidades (16 registros)
5. ✅ academic_setup_carrera (6 registros)
6. ✅ academic_setup_ciclo (48 registros)
7. ✅ academic_setup_periodoacademico (3 registros)
8. ✅ academic_setup_materias (189 registros)
9. ✅ users_docentes (117 registros)
10. ✅ academic_setup_materiaespecialidadesrequeridas (141 registros)
11. ✅ scheduling_bloqueshorariosdefinicion (138 registros)
12. ✅ scheduling_grupos_materias (162 registros)
13. ✅ scheduling_configuracionrestricciones (1 registro)
14. ✅ users_sesionesusuario (0 registros - vacía)

## ❌ Consultas que FALTAN:

Ejecuta estas consultas en PostgreSQL y comparte los resultados:

```sql
-- 1. Tipo de Unidad Académica
SELECT * FROM academic_setup_tipounidadacademica ORDER BY tipo_unidad_id;

-- 2. Secciones
SELECT * FROM academic_setup_seccion ORDER BY seccion_id;

-- 3. Espacios Físicos
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
```

## 📝 Cómo compartir los datos:

1. **Opción A (Recomendada)**: Ejecuta cada consulta y copia/pega los resultados aquí
2. **Opción B**: Exporta como CSV desde pgAdmin y comparte los archivos
3. **Opción C**: Ejecuta todas las consultas y guarda la salida en un archivo de texto

## ⚠️ Importante:

- **NO incluir** `scheduling_horariosasignados` (según tu solicitud)
- Asegúrate de que el encoding sea UTF-8
- Si hay caracteres raros, los limpiaré automáticamente

