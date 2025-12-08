-- ============================================
-- Script SQL para consultar todas las tablas
-- Ejecutar en PostgreSQL y compartir resultados
-- ============================================

-- Configurar encoding
SET client_encoding TO 'UTF8';

-- ============================================
-- 1. auth_user
-- ============================================
SELECT '=== auth_user ===' AS tabla;
SELECT * FROM auth_user ORDER BY id;

-- ============================================
-- 2. academic_setup_tipounidadacademica
-- ============================================
SELECT '=== academic_setup_tipounidadacademica ===' AS tabla;
SELECT * FROM academic_setup_tipounidadacademica ORDER BY tipo_unidad_id;

-- ============================================
-- 3. academic_setup_unidadacademica
-- ============================================
SELECT '=== academic_setup_unidadacademica ===' AS tabla;
SELECT * FROM academic_setup_unidadacademica ORDER BY unidad_id;

-- ============================================
-- 4. academic_setup_tiposespacio
-- ============================================
SELECT '=== academic_setup_tiposespacio ===' AS tabla;
SELECT * FROM academic_setup_tiposespacio ORDER BY tipo_espacio_id;

-- ============================================
-- 5. academic_setup_especialidades
-- ============================================
SELECT '=== academic_setup_especialidades ===' AS tabla;
SELECT * FROM academic_setup_especialidades ORDER BY especialidad_id;

-- ============================================
-- 6. academic_setup_carrera
-- ============================================
SELECT '=== academic_setup_carrera ===' AS tabla;
SELECT * FROM academic_setup_carrera ORDER BY carrera_id;

-- ============================================
-- 7. academic_setup_ciclo
-- ============================================
SELECT '=== academic_setup_ciclo ===' AS tabla;
SELECT * FROM academic_setup_ciclo ORDER BY ciclo_id;

-- ============================================
-- 8. academic_setup_seccion
-- ============================================
SELECT '=== academic_setup_seccion ===' AS tabla;
SELECT * FROM academic_setup_seccion ORDER BY seccion_id;

-- ============================================
-- 9. academic_setup_periodoacademico
-- ============================================
SELECT '=== academic_setup_periodoacademico ===' AS tabla;
SELECT * FROM academic_setup_periodoacademico ORDER BY periodo_id;

-- ============================================
-- 10. academic_setup_materias
-- ============================================
SELECT '=== academic_setup_materias ===' AS tabla;
SELECT * FROM academic_setup_materias ORDER BY materia_id;

-- ============================================
-- 11. academic_setup_espaciosfisicos
-- ============================================
SELECT '=== academic_setup_espaciosfisicos ===' AS tabla;
SELECT * FROM academic_setup_espaciosfisicos ORDER BY espacio_id;

-- ============================================
-- 12. users_roles
-- ============================================
SELECT '=== users_roles ===' AS tabla;
SELECT * FROM users_roles ORDER BY rol_id;

-- ============================================
-- 13. users_docentes
-- ============================================
SELECT '=== users_docentes ===' AS tabla;
SELECT * FROM users_docentes ORDER BY docente_id;

-- ============================================
-- 14. academic_setup_carreramaterias
-- ============================================
SELECT '=== academic_setup_carreramaterias ===' AS tabla;
SELECT * FROM academic_setup_carreramaterias;

-- ============================================
-- 15. academic_setup_materiaespecialidadesrequeridas
-- ============================================
SELECT '=== academic_setup_materiaespecialidadesrequeridas ===' AS tabla;
SELECT * FROM academic_setup_materiaespecialidadesrequeridas;

-- ============================================
-- 16. users_docenteespecialidades
-- ============================================
SELECT '=== users_docenteespecialidades ===' AS tabla;
SELECT * FROM users_docenteespecialidades;

-- ============================================
-- 17. scheduling_bloqueshorariosdefinicion
-- ============================================
SELECT '=== scheduling_bloqueshorariosdefinicion ===' AS tabla;
SELECT * FROM scheduling_bloqueshorariosdefinicion ORDER BY bloque_def_id;

-- ============================================
-- 18. scheduling_grupos
-- ============================================
SELECT '=== scheduling_grupos ===' AS tabla;
SELECT * FROM scheduling_grupos ORDER BY grupo_id;

-- ============================================
-- 19. scheduling_grupos_materias (many-to-many)
-- ============================================
SELECT '=== scheduling_grupos_materias ===' AS tabla;
SELECT * FROM scheduling_grupos_materias ORDER BY grupos_id, materias_id;

-- ============================================
-- 20. scheduling_disponibilidaddocentes
-- ============================================
SELECT '=== scheduling_disponibilidaddocentes ===' AS tabla;
SELECT * FROM scheduling_disponibilidaddocentes ORDER BY disponibilidad_id;

-- ============================================
-- 21. scheduling_configuracionrestricciones
-- ============================================
SELECT '=== scheduling_configuracionrestricciones ===' AS tabla;
SELECT * FROM scheduling_configuracionrestricciones ORDER BY restriccion_id;

-- ============================================
-- 22. users_sesionesusuario
-- ============================================
SELECT '=== users_sesionesusuario ===' AS tabla;
SELECT * FROM users_sesionesusuario ORDER BY sesion_id;

-- ============================================
-- NOTA: HorariosAsignados NO incluido
-- ============================================

