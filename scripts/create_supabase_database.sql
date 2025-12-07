-- ============================================================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS PARA SUPABASE
-- Sistema de Gestión de Horarios - La Pontificia
-- ============================================================================
-- Este script crea todas las tablas, relaciones y restricciones
-- necesarias para replicar la base de datos local en Supabase
-- ============================================================================

-- Configuración inicial
SET timezone = 'America/Lima';
SET client_encoding = 'UTF8';

-- ============================================================================
-- ELIMINAR TABLAS EXISTENTES (SOLO PARA DESARROLLO - COMENTAR EN PRODUCCIÓN)
-- ============================================================================
-- ⚠️ ADVERTENCIA: Descomentar estas líneas solo si quieres limpiar la BD
-- DROP TABLE IF EXISTS scheduling_horariosasignados CASCADE;
-- DROP TABLE IF EXISTS scheduling_disponibilidaddocentes CASCADE;
-- DROP TABLE IF EXISTS scheduling_configuracionrestricciones CASCADE;
-- DROP TABLE IF EXISTS scheduling_grupos_materias CASCADE;
-- DROP TABLE IF EXISTS scheduling_grupos CASCADE;
-- DROP TABLE IF EXISTS scheduling_bloqueshorariosdefinicion CASCADE;
-- DROP TABLE IF EXISTS users_sesionesusuario CASCADE;
-- DROP TABLE IF EXISTS users_docenteespecialidades CASCADE;
-- DROP TABLE IF EXISTS users_docentes CASCADE;
-- DROP TABLE IF EXISTS users_roles CASCADE;
-- DROP TABLE IF EXISTS academic_setup_materiaespecialidadesrequeridas CASCADE;
-- DROP TABLE IF EXISTS academic_setup_carreramaterias CASCADE;
-- DROP TABLE IF EXISTS academic_setup_materias CASCADE;
-- DROP TABLE IF EXISTS academic_setup_espaciosfisicos CASCADE;
-- DROP TABLE IF EXISTS academic_setup_seccion CASCADE;
-- DROP TABLE IF EXISTS academic_setup_ciclo CASCADE;
-- DROP TABLE IF EXISTS academic_setup_especialidades CASCADE;
-- DROP TABLE IF EXISTS academic_setup_tiposespacio CASCADE;
-- DROP TABLE IF EXISTS academic_setup_periodoacademico CASCADE;
-- DROP TABLE IF EXISTS academic_setup_carrera CASCADE;
-- DROP TABLE IF EXISTS academic_setup_unidadacademica CASCADE;
-- DROP TABLE IF EXISTS academic_setup_tipounidadacademica CASCADE;

-- ============================================================================
-- MÓDULO 1: ACADEMIC SETUP
-- ============================================================================

-- Tabla: Tipo de Unidad Académica
CREATE TABLE IF NOT EXISTS academic_setup_tipounidadacademica (
    tipo_unidad_id SERIAL PRIMARY KEY,
    nombre_tipo VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla: Unidad Académica
CREATE TABLE IF NOT EXISTS academic_setup_unidadacademica (
    unidad_id SERIAL PRIMARY KEY,
    nombre_unidad VARCHAR(255) NOT NULL UNIQUE,
    descripcion TEXT,
    tipo_unidad_id INTEGER REFERENCES academic_setup_tipounidadacademica(tipo_unidad_id) ON DELETE SET NULL
);

-- Tabla: Carrera
CREATE TABLE IF NOT EXISTS academic_setup_carrera (
    carrera_id SERIAL PRIMARY KEY,
    nombre_carrera VARCHAR(255) NOT NULL,
    codigo_carrera VARCHAR(20) UNIQUE,
    horas_totales_curricula INTEGER,
    unidad_id INTEGER NOT NULL REFERENCES academic_setup_unidadacademica(unidad_id) ON DELETE RESTRICT,
    CONSTRAINT unique_carrera_unidad UNIQUE (nombre_carrera, unidad_id)
);

-- Tabla: Ciclo
CREATE TABLE IF NOT EXISTS academic_setup_ciclo (
    ciclo_id SERIAL PRIMARY KEY,
    nombre_ciclo VARCHAR(100) NOT NULL,
    orden INTEGER NOT NULL,
    carrera_id INTEGER NOT NULL REFERENCES academic_setup_carrera(carrera_id) ON DELETE CASCADE,
    CONSTRAINT unique_ciclo_carrera_orden UNIQUE (carrera_id, orden)
);

-- Tabla: Sección
CREATE TABLE IF NOT EXISTS academic_setup_seccion (
    seccion_id SERIAL PRIMARY KEY,
    nombre_seccion VARCHAR(100) NOT NULL,
    capacidad INTEGER,
    ciclo_id INTEGER NOT NULL REFERENCES academic_setup_ciclo(ciclo_id) ON DELETE CASCADE,
    CONSTRAINT unique_seccion_ciclo UNIQUE (nombre_seccion, ciclo_id)
);

-- Tabla: Período Académico
CREATE TABLE IF NOT EXISTS academic_setup_periodoacademico (
    periodo_id SERIAL PRIMARY KEY,
    nombre_periodo VARCHAR(50) NOT NULL UNIQUE,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabla: Tipos de Espacio
CREATE TABLE IF NOT EXISTS academic_setup_tiposespacio (
    tipo_espacio_id SERIAL PRIMARY KEY,
    nombre_tipo_espacio VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla: Espacios Físicos
CREATE TABLE IF NOT EXISTS academic_setup_espaciosfisicos (
    espacio_id SERIAL PRIMARY KEY,
    nombre_espacio VARCHAR(100) NOT NULL,
    tipo_espacio_id INTEGER NOT NULL REFERENCES academic_setup_tiposespacio(tipo_espacio_id) ON DELETE RESTRICT,
    capacidad INTEGER,
    ubicacion VARCHAR(255),
    recursos_adicionales TEXT,
    unidad_id INTEGER REFERENCES academic_setup_unidadacademica(unidad_id) ON DELETE SET NULL,
    CONSTRAINT unique_espacio_unidad UNIQUE (nombre_espacio, unidad_id)
);

-- Tabla: Especialidades
CREATE TABLE IF NOT EXISTS academic_setup_especialidades (
    especialidad_id SERIAL PRIMARY KEY,
    nombre_especialidad VARCHAR(150) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla: Materias
CREATE TABLE IF NOT EXISTS academic_setup_materias (
    materia_id SERIAL PRIMARY KEY,
    codigo_materia VARCHAR(50) NOT NULL UNIQUE,
    nombre_materia VARCHAR(255) NOT NULL,
    descripcion TEXT,
    horas_academicas_teoricas INTEGER NOT NULL DEFAULT 0,
    horas_academicas_practicas INTEGER NOT NULL DEFAULT 0,
    horas_academicas_laboratorio INTEGER NOT NULL DEFAULT 0,
    requiere_tipo_espacio_especifico_id INTEGER REFERENCES academic_setup_tiposespacio(tipo_espacio_id) ON DELETE SET NULL,
    estado BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabla: Carrera-Materias (Many-to-Many)
CREATE TABLE IF NOT EXISTS academic_setup_carreramaterias (
    id SERIAL PRIMARY KEY,
    carrera_id INTEGER NOT NULL REFERENCES academic_setup_carrera(carrera_id) ON DELETE CASCADE,
    materia_id INTEGER NOT NULL REFERENCES academic_setup_materias(materia_id) ON DELETE CASCADE,
    ciclo_id INTEGER REFERENCES academic_setup_ciclo(ciclo_id) ON DELETE CASCADE,
    ciclo_sugerido INTEGER,
    CONSTRAINT unique_carrera_materia_ciclo UNIQUE (carrera_id, materia_id, ciclo_id)
);

-- Tabla: Materia-Especialidades Requeridas (Many-to-Many)
CREATE TABLE IF NOT EXISTS academic_setup_materiaespecialidadesrequeridas (
    id SERIAL PRIMARY KEY,
    materia_id INTEGER NOT NULL REFERENCES academic_setup_materias(materia_id) ON DELETE CASCADE,
    especialidad_id INTEGER NOT NULL REFERENCES academic_setup_especialidades(especialidad_id) ON DELETE CASCADE,
    CONSTRAINT unique_materia_especialidad UNIQUE (materia_id, especialidad_id)
);

-- ============================================================================
-- MÓDULO 2: USERS
-- ============================================================================

-- Tabla: Roles
CREATE TABLE IF NOT EXISTS users_roles (
    rol_id SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla: Docentes
CREATE TABLE IF NOT EXISTS users_docentes (
    docente_id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE REFERENCES auth_user(id) ON DELETE SET NULL,
    codigo_docente VARCHAR(50) UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    dni VARCHAR(15) UNIQUE,
    email VARCHAR(254) UNIQUE,
    telefono VARCHAR(30),
    tipo_contrato VARCHAR(50),
    max_horas_semanales INTEGER,
    unidad_principal_id INTEGER REFERENCES academic_setup_unidadacademica(unidad_id) ON DELETE SET NULL
);

-- Tabla: Docente-Especialidades (Many-to-Many)
CREATE TABLE IF NOT EXISTS users_docenteespecialidades (
    id SERIAL PRIMARY KEY,
    docente_id INTEGER NOT NULL REFERENCES users_docentes(docente_id) ON DELETE CASCADE,
    especialidad_id INTEGER NOT NULL REFERENCES academic_setup_especialidades(especialidad_id) ON DELETE CASCADE,
    CONSTRAINT unique_docente_especialidad UNIQUE (docente_id, especialidad_id)
);

-- Tabla: Sesiones de Usuario
CREATE TABLE IF NOT EXISTS users_sesionesusuario (
    sesion_id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL UNIQUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address INET,
    user_agent TEXT
);

-- ============================================================================
-- MÓDULO 3: SCHEDULING
-- ============================================================================

-- Tabla: Bloques Horarios Definición
CREATE TABLE IF NOT EXISTS scheduling_bloqueshorariosdefinicion (
    bloque_def_id SERIAL PRIMARY KEY,
    nombre_bloque VARCHAR(50) NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    turno VARCHAR(1) NOT NULL CHECK (turno IN ('M', 'T', 'N')),
    dia_semana INTEGER CHECK (dia_semana BETWEEN 1 AND 7),
    CONSTRAINT unique_bloque_completo UNIQUE (nombre_bloque, hora_inicio, hora_fin, turno, dia_semana)
);

-- Tabla: Grupos
CREATE TABLE IF NOT EXISTS scheduling_grupos (
    grupo_id SERIAL PRIMARY KEY,
    codigo_grupo VARCHAR(50) NOT NULL,
    carrera_id INTEGER NOT NULL REFERENCES academic_setup_carrera(carrera_id) ON DELETE CASCADE,
    periodo_id INTEGER NOT NULL REFERENCES academic_setup_periodoacademico(periodo_id) ON DELETE CASCADE,
    numero_estudiantes_estimado INTEGER,
    turno_preferente VARCHAR(1) CHECK (turno_preferente IN ('M', 'T', 'N')),
    docente_asignado_directamente_id INTEGER REFERENCES users_docentes(docente_id) ON DELETE SET NULL,
    ciclo_semestral INTEGER,
    CONSTRAINT unique_grupo_periodo UNIQUE (codigo_grupo, periodo_id)
);

-- Tabla: Grupos-Materias (Many-to-Many)
CREATE TABLE IF NOT EXISTS scheduling_grupos_materias (
    id SERIAL PRIMARY KEY,
    grupos_id INTEGER NOT NULL REFERENCES scheduling_grupos(grupo_id) ON DELETE CASCADE,
    materias_id INTEGER NOT NULL REFERENCES academic_setup_materias(materia_id) ON DELETE CASCADE,
    CONSTRAINT unique_grupo_materia UNIQUE (grupos_id, materias_id)
);

-- Tabla: Disponibilidad Docentes
CREATE TABLE IF NOT EXISTS scheduling_disponibilidaddocentes (
    disponibilidad_id SERIAL PRIMARY KEY,
    docente_id INTEGER NOT NULL REFERENCES users_docentes(docente_id) ON DELETE CASCADE,
    periodo_id INTEGER NOT NULL REFERENCES academic_setup_periodoacademico(periodo_id) ON DELETE CASCADE,
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
    bloque_horario_id INTEGER NOT NULL REFERENCES scheduling_bloqueshorariosdefinicion(bloque_def_id) ON DELETE CASCADE,
    esta_disponible BOOLEAN NOT NULL DEFAULT TRUE,
    preferencia SMALLINT NOT NULL DEFAULT 0,
    origen_carga VARCHAR(10) NOT NULL DEFAULT 'MANUAL' CHECK (origen_carga IN ('MANUAL', 'EXCEL')),
    CONSTRAINT unique_disponibilidad UNIQUE (docente_id, periodo_id, dia_semana, bloque_horario_id)
);

-- Tabla: Horarios Asignados
CREATE TABLE IF NOT EXISTS scheduling_horariosasignados (
    horario_id SERIAL PRIMARY KEY,
    grupo_id INTEGER NOT NULL REFERENCES scheduling_grupos(grupo_id) ON DELETE CASCADE,
    materia_id INTEGER REFERENCES academic_setup_materias(materia_id) ON DELETE CASCADE,
    docente_id INTEGER NOT NULL REFERENCES users_docentes(docente_id) ON DELETE CASCADE,
    espacio_id INTEGER NOT NULL REFERENCES academic_setup_espaciosfisicos(espacio_id) ON DELETE CASCADE,
    periodo_id INTEGER NOT NULL REFERENCES academic_setup_periodoacademico(periodo_id) ON DELETE CASCADE,
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
    bloque_horario_id INTEGER NOT NULL REFERENCES scheduling_bloqueshorariosdefinicion(bloque_def_id) ON DELETE CASCADE,
    estado VARCHAR(50) NOT NULL DEFAULT 'Programado' CHECK (estado IN ('Programado', 'Confirmado', 'Cancelado')),
    observaciones TEXT,
    -- Restricciones de unicidad para evitar conflictos
    CONSTRAINT unique_docente_horario UNIQUE (docente_id, periodo_id, dia_semana, bloque_horario_id),
    CONSTRAINT unique_espacio_horario UNIQUE (espacio_id, periodo_id, dia_semana, bloque_horario_id),
    CONSTRAINT unique_grupo_horario UNIQUE (grupo_id, periodo_id, dia_semana, bloque_horario_id),
    CONSTRAINT unique_grupo_materia_horario UNIQUE (grupo_id, materia_id, periodo_id, dia_semana, bloque_horario_id)
);

-- Tabla: Configuración de Restricciones
CREATE TABLE IF NOT EXISTS scheduling_configuracionrestricciones (
    restriccion_id SERIAL PRIMARY KEY,
    codigo_restriccion VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    tipo_aplicacion VARCHAR(50) NOT NULL CHECK (tipo_aplicacion IN ('GLOBAL', 'DOCENTE', 'MATERIA', 'AULA', 'CARRERA', 'PERIODO')),
    entidad_id_1 INTEGER,
    entidad_id_2 INTEGER,
    valor_parametro VARCHAR(255),
    periodo_aplicable_id INTEGER REFERENCES academic_setup_periodoacademico(periodo_id) ON DELETE CASCADE,
    esta_activa BOOLEAN NOT NULL DEFAULT TRUE
);

-- ============================================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ============================================================================

-- Índices para búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_carrera_unidad ON academic_setup_carrera(unidad_id);
CREATE INDEX IF NOT EXISTS idx_ciclo_carrera ON academic_setup_ciclo(carrera_id);
CREATE INDEX IF NOT EXISTS idx_seccion_ciclo ON academic_setup_seccion(ciclo_id);
CREATE INDEX IF NOT EXISTS idx_espacio_tipo ON academic_setup_espaciosfisicos(tipo_espacio_id);
CREATE INDEX IF NOT EXISTS idx_espacio_unidad ON academic_setup_espaciosfisicos(unidad_id);
CREATE INDEX IF NOT EXISTS idx_docente_usuario ON users_docentes(usuario_id);
CREATE INDEX IF NOT EXISTS idx_docente_unidad ON users_docentes(unidad_principal_id);
CREATE INDEX IF NOT EXISTS idx_grupo_carrera ON scheduling_grupos(carrera_id);
CREATE INDEX IF NOT EXISTS idx_grupo_periodo ON scheduling_grupos(periodo_id);
CREATE INDEX IF NOT EXISTS idx_disponibilidad_docente ON scheduling_disponibilidaddocentes(docente_id);
CREATE INDEX IF NOT EXISTS idx_disponibilidad_periodo ON scheduling_disponibilidaddocentes(periodo_id);
CREATE INDEX IF NOT EXISTS idx_horario_docente ON scheduling_horariosasignados(docente_id);
CREATE INDEX IF NOT EXISTS idx_horario_espacio ON scheduling_horariosasignados(espacio_id);
CREATE INDEX IF NOT EXISTS idx_horario_grupo ON scheduling_horariosasignados(grupo_id);
CREATE INDEX IF NOT EXISTS idx_horario_periodo ON scheduling_horariosasignados(periodo_id);
CREATE INDEX IF NOT EXISTS idx_horario_bloque ON scheduling_horariosasignados(bloque_horario_id);

-- ============================================================================
-- VERIFICACIONES Y VALIDACIONES
-- ============================================================================

-- Función para verificar la estructura de la base de datos
CREATE OR REPLACE FUNCTION verificar_estructura_bd()
RETURNS TABLE (
    tabla TEXT,
    columnas INTEGER,
    restricciones INTEGER,
    indices INTEGER,
    estado TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.table_name::TEXT as tabla,
        COUNT(DISTINCT c.column_name)::INTEGER as columnas,
        COUNT(DISTINCT tc.constraint_name)::INTEGER as restricciones,
        COUNT(DISTINCT i.indexname)::INTEGER as indices,
        CASE 
            WHEN COUNT(DISTINCT c.column_name) > 0 THEN 'OK'
            ELSE 'ERROR'
        END::TEXT as estado
    FROM information_schema.tables t
    LEFT JOIN information_schema.columns c ON t.table_name = c.table_name
    LEFT JOIN information_schema.table_constraints tc ON t.table_name = tc.table_name
    LEFT JOIN pg_indexes i ON t.table_name = i.tablename
    WHERE t.table_schema = 'public'
        AND t.table_name LIKE 'academic_setup_%'
        OR t.table_name LIKE 'users_%'
        OR t.table_name LIKE 'scheduling_%'
    GROUP BY t.table_name
    ORDER BY t.table_name;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SCRIPT DE VERIFICACIÓN
-- ============================================================================

-- Verificar que todas las tablas existen
DO $$
DECLARE
    tablas_requeridas TEXT[] := ARRAY[
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
    ];
    tabla TEXT;
    existe BOOLEAN;
    faltantes TEXT[] := ARRAY[]::TEXT[];
BEGIN
    FOREACH tabla IN ARRAY tablas_requeridas
    LOOP
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = tabla
        ) INTO existe;
        
        IF NOT existe THEN
            faltantes := array_append(faltantes, tabla);
        END IF;
    END LOOP;
    
    IF array_length(faltantes, 1) > 0 THEN
        RAISE WARNING 'Tablas faltantes: %', array_to_string(faltantes, ', ');
    ELSE
        RAISE NOTICE '✓ Todas las tablas requeridas existen';
    END IF;
END $$;

-- Verificar Foreign Keys
DO $$
DECLARE
    fk_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO fk_count
    FROM information_schema.table_constraints
    WHERE constraint_type = 'FOREIGN KEY'
    AND table_schema = 'public'
    AND (table_name LIKE 'academic_setup_%' 
         OR table_name LIKE 'users_%' 
         OR table_name LIKE 'scheduling_%');
    
    RAISE NOTICE '✓ Total de Foreign Keys encontrados: %', fk_count;
    
    IF fk_count < 20 THEN
        RAISE WARNING 'Puede haber Foreign Keys faltantes. Esperado: ~25, Encontrado: %', fk_count;
    END IF;
END $$;

-- Verificar Constraints de Unicidad
DO $$
DECLARE
    unique_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO unique_count
    FROM information_schema.table_constraints
    WHERE constraint_type = 'UNIQUE'
    AND table_schema = 'public'
    AND (table_name LIKE 'academic_setup_%' 
         OR table_name LIKE 'users_%' 
         OR table_name LIKE 'scheduling_%');
    
    RAISE NOTICE '✓ Total de Constraints UNIQUE encontrados: %', unique_count;
END $$;

-- ============================================================================
-- MENSAJE FINAL
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE '✓ Script de creación de base de datos ejecutado correctamente';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Para verificar la estructura completa, ejecuta:';
    RAISE NOTICE '  SELECT * FROM verificar_estructura_bd();';
    RAISE NOTICE '';
    RAISE NOTICE 'Para ver todas las tablas creadas:';
    RAISE NOTICE '  SELECT table_name FROM information_schema.tables WHERE table_schema = ''public'' ORDER BY table_name;';
    RAISE NOTICE '';
END $$;

