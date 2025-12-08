-- ============================================================================
-- SCRIPT DE VERIFICACIÓN DE BASE DE DATOS EN SUPABASE
-- Sistema de Gestión de Horarios - La Pontificia
-- ============================================================================
-- Este script verifica que todas las tablas, relaciones y restricciones
-- estén correctamente creadas en Supabase
-- ============================================================================

-- ============================================================================
-- 1. VERIFICAR EXISTENCIA DE TABLAS
-- ============================================================================

SELECT 
    'Verificación de Tablas' as seccion,
    table_name as tabla,
    CASE 
        WHEN table_name IS NOT NULL THEN '✓ Existe'
        ELSE '✗ Faltante'
    END as estado
FROM (
    SELECT unnest(ARRAY[
        'academic_setup_tipounidadacademica',
        'academic_setup_unidadacademica',
        'academic_setup_carrera',
        'academic_setup_ciclo',
        'academic_setup_seccion',
        'academic_setup_periodoacademico',
        'academic_setup_tiposespacio',
        'academic_setup_espaciosfisicos',
        'academic_setup_especialidades',
        'academic_setup_materias',
        'academic_setup_carreramaterias',
        'academic_setup_materiaespecialidadesrequeridas',
        'users_roles',
        'users_docentes',
        'users_docenteespecialidades',
        'users_sesionesusuario',
        'scheduling_bloqueshorariosdefinicion',
        'scheduling_grupos',
        'scheduling_grupos_materias',
        'scheduling_disponibilidaddocentes',
        'scheduling_horariosasignados',
        'scheduling_configuracionrestricciones'
    ]) as table_name
) t
LEFT JOIN information_schema.tables it 
    ON t.table_name = it.table_name 
    AND it.table_schema = 'public'
ORDER BY t.table_name;

-- ============================================================================
-- 2. VERIFICAR FOREIGN KEYS
-- ============================================================================

SELECT 
    'Foreign Keys' as seccion,
    tc.table_name as tabla,
    kcu.column_name as columna,
    ccu.table_name AS tabla_referenciada,
    ccu.column_name AS columna_referenciada,
    tc.constraint_name as constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND (tc.table_name LIKE 'academic_setup_%' 
         OR tc.table_name LIKE 'users_%' 
         OR tc.table_name LIKE 'scheduling_%')
ORDER BY tc.table_name, kcu.column_name;

-- ============================================================================
-- 3. VERIFICAR CONSTRAINTS UNIQUE
-- ============================================================================

SELECT 
    'Constraints UNIQUE' as seccion,
    tc.table_name as tabla,
    tc.constraint_name as constraint_name,
    string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columnas
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'UNIQUE'
    AND tc.table_schema = 'public'
    AND (tc.table_name LIKE 'academic_setup_%' 
         OR tc.table_name LIKE 'users_%' 
         OR tc.table_name LIKE 'scheduling_%')
GROUP BY tc.table_name, tc.constraint_name
ORDER BY tc.table_name;

-- ============================================================================
-- 4. VERIFICAR CHECK CONSTRAINTS
-- ============================================================================

SELECT 
    'Check Constraints' as seccion,
    tc.table_name as tabla,
    tc.constraint_name as constraint_name,
    cc.check_clause as condicion
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc
    ON tc.constraint_name = cc.constraint_name
WHERE tc.constraint_type = 'CHECK'
    AND tc.table_schema = 'public'
    AND (tc.table_name LIKE 'academic_setup_%' 
         OR tc.table_name LIKE 'users_%' 
         OR tc.table_name LIKE 'scheduling_%')
ORDER BY tc.table_name;

-- ============================================================================
-- 5. VERIFICAR ÍNDICES
-- ============================================================================

SELECT 
    'Índices' as seccion,
    tablename as tabla,
    indexname as indice,
    indexdef as definicion
FROM pg_indexes
WHERE schemaname = 'public'
    AND (tablename LIKE 'academic_setup_%' 
         OR tablename LIKE 'users_%' 
         OR tablename LIKE 'scheduling_%')
ORDER BY tablename, indexname;

-- ============================================================================
-- 6. RESUMEN DE ESTRUCTURA
-- ============================================================================

SELECT 
    'RESUMEN' as seccion,
    'Total Tablas' as concepto,
    COUNT(*)::TEXT as valor
FROM information_schema.tables
WHERE table_schema = 'public'
    AND (table_name LIKE 'academic_setup_%' 
         OR table_name LIKE 'users_%' 
         OR table_name LIKE 'scheduling_%')

UNION ALL

SELECT 
    'RESUMEN',
    'Total Foreign Keys',
    COUNT(*)::TEXT
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY'
    AND table_schema = 'public'
    AND (table_name LIKE 'academic_setup_%' 
         OR table_name LIKE 'users_%' 
         OR table_name LIKE 'scheduling_%')

UNION ALL

SELECT 
    'RESUMEN',
    'Total Constraints UNIQUE',
    COUNT(*)::TEXT
FROM information_schema.table_constraints
WHERE constraint_type = 'UNIQUE'
    AND table_schema = 'public'
    AND (table_name LIKE 'academic_setup_%' 
         OR table_name LIKE 'users_%' 
         OR table_name LIKE 'scheduling_%')

UNION ALL

SELECT 
    'RESUMEN',
    'Total Índices',
    COUNT(*)::TEXT
FROM pg_indexes
WHERE schemaname = 'public'
    AND (tablename LIKE 'academic_setup_%' 
         OR tablename LIKE 'users_%' 
         OR tablename LIKE 'scheduling_%');

-- ============================================================================
-- 7. VERIFICAR COLUMNAS ESPECÍFICAS IMPORTANTES
-- ============================================================================

SELECT 
    'Columnas Importantes' as seccion,
    table_name as tabla,
    column_name as columna,
    data_type as tipo_dato,
    is_nullable as permite_null,
    column_default as valor_default
FROM information_schema.columns
WHERE table_schema = 'public'
    AND (
        (table_name = 'users_docentes' AND column_name IN ('dni', 'email', 'codigo_docente'))
        OR (table_name = 'academic_setup_materias' AND column_name = 'codigo_materia')
        OR (table_name = 'academic_setup_carrera' AND column_name = 'codigo_carrera')
        OR (table_name = 'scheduling_horariosasignados' AND column_name IN ('docente_id', 'espacio_id', 'grupo_id'))
    )
ORDER BY table_name, column_name;

-- ============================================================================
-- FIN DEL SCRIPT DE VERIFICACIÓN
-- ============================================================================


