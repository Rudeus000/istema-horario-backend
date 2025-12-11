-- ============================================
-- CONSULTAS FALTANTES - Ejecutar UNA POR UNA
-- ============================================

-- 4. Roles
SELECT * FROM users_roles ORDER BY rol_id;

-- 5. Carrera-Materias (relación)
SELECT * FROM academic_setup_carreramaterias;

-- 6. Docente-Especialidades (relación)
SELECT * FROM users_docenteespecialidades;

-- 7. Grupos (EJECUTAR COMPLETO - copia toda la línea)
SELECT * FROM scheduling_grupos ORDER BY grupo_id;

-- 8. Disponibilidad Docentes
SELECT * FROM scheduling_disponibilidaddocentes ORDER BY disponibilidad_id;

