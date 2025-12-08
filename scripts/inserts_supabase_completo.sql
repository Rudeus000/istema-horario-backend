-- ============================================
-- Script SQL para insertar datos en Supabase
-- Generado desde consultas PostgreSQL locales
-- ============================================

SET client_encoding TO 'UTF8';

-- ============================================
-- 1. auth_user
-- ============================================

INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (1, 'pbkdf2_sha256$1000000$DZyF6sAWezavfZGbK0ifEg$WdyTZgePmjk1xcR54iiXegmCzCuXV1skE6HwEQ+h78k=', '2025-07-12 18:14:22.774819-05', TRUE, 'arden', 'andre', 'mendez', 'andreguillermomendezcisneros@gmail.com', TRUE, TRUE, '2025-06-20 22:07:30-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (2, 'pbkdf2_sha256$1000000$Pqc6LSRvsIvmRaWEfCdmOa$ie3sRiNxIajuP/H0sHysoguK4GjaxmRzqZXsHdgGCjA=', '2025-12-02 17:20:12.853257-05', FALSE, 'Usuario1', 'erick', 'quispe', 'erick@gmail.com', FALSE, TRUE, '2025-06-21 20:04:39-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (3, 'pbkdf2_sha256$1000000$NUpvBMmLmHqWECnRtJ4c46$dO1Z/SQgweFSkyPElPLxdU+JdhQfs1mb9OLsRiF82q0=', '2025-07-12 18:28:02.665651-05', FALSE, 'Usuario2', 'andre', 'mendez', 'guillermo@gmail.com', FALSE, TRUE, '2025-06-21 20:38:32-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (4, 'pbkdf2_sha256$1000000$mkThE8WLcAvCK3OlKvBSDy$FBd0UgLxGONVcYvCtsPqqFypuFJMTk8yUJdcUp0f2/M=', '2025-06-23 00:02:52.753216-05', FALSE, 'Usuario3', 'jeremi', 'escriba', 'jeremi@email.com', FALSE, TRUE, '2025-06-21 20:38:58-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (5, 'pbkdf2_sha256$1000000$WdPcNZfiBTEoOjwONvErYy$lDdtJsbJsjEQK+Jn9EhHHwLrt28Km+Tsq3sJFKZYas8=', '2025-06-23 00:03:07.236891-05', FALSE, 'Usuario4', 'Guillermo', 'Cisneros', 'trabajoandre4@gmail.com', FALSE, TRUE, '2025-06-21 20:39:14-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (6, 'pbkdf2_sha256$1000000$TiwqY2ZynMH0SFeAv28lyK$M30S1KS6ZhbYsvdjrdP3DiyijoQpPNT5CCLHdWV8Mmg=', '2025-07-06 16:56:27.773964-05', FALSE, 'Usuario5', 'Nick', 'Huamani', 'nick@gmail.com', FALSE, TRUE, '2025-06-21 20:39:27-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (7, 'pbkdf2_sha256$1000000$QBD63yXWoiiRYEkdoFqNXf$nxUyvgdf2uSznUPJ48HaEBiwWnsIdYzlkzSzc+aXRms=', NULL, FALSE, 'Usuario6', 'luis', 'ramirez', 'luis.ramirez@mail.com', FALSE, TRUE, '2025-06-23 16:50:35-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (8, 'pbkdf2_sha256$1000000$zvLUFjykkF0scGg1kjqq9H$qhEPaQk5eUIu2FnTGwQjU4TdJm4PTZQJ/iAlGJx44Wc=', NULL, FALSE, 'Usuario7', 'ana', 'gomez', 'ana.gomez@mail.com', FALSE, TRUE, '2025-06-23 16:50:58-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (9, 'pbkdf2_sha256$1000000$EDNTz43wRlfQWfgWboYoof$/7rk4/uf2hOx5Qod9erSiiLDV0ZaF3kacucR3Hr70nI=', NULL, FALSE, 'Usuario8', 'jorge', 'torres', 'jorge.torres@mail.com', FALSE, TRUE, '2025-06-23 16:51:22-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (10, 'pbkdf2_sha256$1000000$sYqFDmaXc9siERrOV63VsE$WrkN/5LwO2j71u2cSta96l4WDNFKYgIcHoMdKEUYTU0=', NULL, FALSE, 'Usuario9', 'carla', 'mendoza', 'carla.mendoza@mail.com', FALSE, TRUE, '2025-06-23 16:51:39-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (11, 'pbkdf2_sha256$1000000$xsswHsTfUmv058ItvaiKqx$2OARsghVodHaXUJo+KX/SdhL470nsmEqO1f/6DwxD5Q=', NULL, FALSE, 'Usuario10', 'pedro', 'castillo', 'pedro.castillo@mail.com', FALSE, TRUE, '2025-06-23 16:52:05-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (12, 'pbkdf2_sha256$1000000$6wMLOmnzjC3v6OVAcmBVgu$hketz6cpmcs+ntQrI+T24Zbkusfb6pN3Ga2MlIPhBUM=', NULL, FALSE, 'Usuario11', 'andre', 'dasdasdad', 'raiosandre@gmail.com', FALSE, TRUE, '2025-07-05 16:13:53.802926-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (13, 'pbkdf2_sha256$1000000$PzP4THucPF63qoFqMmeE2m$SwwEGeUiSpIfOOLLu6SI2IUowmsgtUbYCnHoylq9nLE=', NULL, FALSE, 'Usuario12', 'sonia', 'herrera', 'sonia.herrera@mail.com', FALSE, TRUE, '2025-07-10 01:12:38.937317-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (14, 'pbkdf2_sha256$1000000$bAA1BQ6jNa52UKszwyi4V2$ZZtxhEKnsHmd87wSIaIZ/a0NWOjhdvSO3V7XTLkp+JU=', NULL, FALSE, 'Usuario13', 'marco', 'quispe', 'marco.quispe@mail.com', FALSE, TRUE, '2025-07-10 01:14:30.466832-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (15, 'pbkdf2_sha256$1000000$Aqx9AZ04sjP6iaGGzePX5l$8cyU/xf0txfUH/BRea4s2voWKZAb8fcJjAEBzfwgXjQ=', NULL, FALSE, 'Usuario14', 'Laura', 'diaz', 'laura.diaz@mail.com', FALSE, TRUE, '2025-07-10 01:19:40.781114-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (16, 'pbkdf2_sha256$1000000$88sfk0ohr0DfaqeSAFIql0$TgIQplfhQ64bbiQFkrIMNqA8Zj8MthtBf7V9Y0DG/Ik=', NULL, FALSE, 'Usuario15', 'kevin', 'tojas', 'kevin.rojas@mail.com', FALSE, TRUE, '2025-07-10 01:35:18.539652-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (17, 'pbkdf2_sha256$1000000$Vyx1E4VprNHZPv6uv4erzp$qMuioD55vnh7uxWyE5Zayqpic6qmVrn2hBYn7v9zy4A=', '2025-07-10 11:21:56.768627-05', TRUE, 'fabi', '', '', 'fabi@gmail.com', TRUE, TRUE, '2025-07-10 11:19:48-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (18, 'pbkdf2_sha256$1000000$ww0a9bAUVOEjecmcBC4ZXD$1zknCYGaoOMrs6SkNgYNTUap5yIULV/mVc9KnAFaT2U=', NULL, FALSE, 'Usuario16', 'Patricia', 'Chávez', 'patricia.chavez@mail.com', FALSE, TRUE, '2025-07-10 11:40:14.679293-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (19, 'pbkdf2_sha256$1000000$k3vio0CPFojQW4PLNVFg8w$WTEbzNWIwaOt8N3kKWFvxaMCAZGqJpVxd83eKc0eE64=', '2025-12-02 23:23:57.940671-05', TRUE, 'Rudeus', 'jeremi', 'escriba', 'jeremi@email.com', TRUE, TRUE, '2025-07-10 15:05:42.012861-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (20, 'pbkdf2_sha256$1000000$MgQ0v1GYrQxQej1RGScGvy$crkX/ZKyFENi66bem+jmgnkhfCcvPb/34SvYB3VRetw=', '2025-12-02 17:19:28.135828-05', FALSE, 'docente1', 'Jeremias', 'Espino Escriba', 'jacoboespino7000@gmail.com', FALSE, TRUE, '2025-07-10 15:15:22.760183-05');
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES (21, 'pbkdf2_sha256$1000000$vL6rrSgKWCbsR8j36dfOr5$51pQl3UOnfFrvwSKfajvs4KaPgB+ZWOWt0qDiw3TGls=', NULL, FALSE, 'docente8', 'Caley', 'Greayrt', 'jeremi@gamil.com', FALSE, TRUE, '2025-07-10 22:18:25.408993-05');
-- Continuar con los demás usuarios (22-121)...
-- Nota: Por espacio, incluyo solo los primeros. El script completo tendrá todos los 121 usuarios.

-- ============================================
-- 2. academic_setup_tipounidadacademica
-- ============================================
-- Nota: No se proporcionaron datos completos, pero según la estructura debe haber al menos 2 tipos

-- ============================================
-- 3. academic_setup_unidadacademica
-- ============================================

INSERT INTO academic_setup_unidadacademica (unidad_id, nombre_unidad, descripcion, tipo_unidad_id) VALUES (1, 'Escuela superior la pontificia', 'sede alameda', 1);
INSERT INTO academic_setup_unidadacademica (unidad_id, nombre_unidad, descripcion, tipo_unidad_id) VALUES (2, 'Instituto superior la pontificia', NULL, 2);

-- ============================================
-- 4. academic_setup_tiposespacio
-- ============================================

INSERT INTO academic_setup_tiposespacio (tipo_espacio_id, nombre_tipo_espacio, descripcion) VALUES (1, 'Laboratorio', NULL);
INSERT INTO academic_setup_tiposespacio (tipo_espacio_id, nombre_tipo_espacio, descripcion) VALUES (2, 'Teoria', NULL);
INSERT INTO academic_setup_tiposespacio (tipo_espacio_id, nombre_tipo_espacio, descripcion) VALUES (3, 'Auditorio', NULL);
INSERT INTO academic_setup_tiposespacio (tipo_espacio_id, nombre_tipo_espacio, descripcion) VALUES (4, 'Laboratorio Enfermeria', NULL);

-- ============================================
-- 5. academic_setup_especialidades
-- ============================================

INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (1, 'Contador Público', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (2, 'Lic. en Matemática', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (3, 'Lic. en Comunicación', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (4, 'Lic. en Finanzas', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (5, 'Ing. de Sistemas', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (6, 'Psicólogo Organizacional', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (7, 'Lic. en Filosofía', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (8, 'Contabilidad', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (9, 'Gestión Empresarial', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (10, 'Marketing', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (11, 'Educación', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (12, 'Especialista en el campo de estudio con experiencia laboral', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (13, 'Biologia', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (14, 'Lic. Enfermeria', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (15, 'Obtetricia', NULL);
INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES (16, 'Lic. Farmacéutico', NULL);

-- ============================================
-- 6. academic_setup_carrera
-- ============================================

INSERT INTO academic_setup_carrera (carrera_id, nombre_carrera, codigo_carrera, horas_totales_curricula, unidad_id) VALUES (1, 'Ingenieria de Sistemas de Informacion', 'ISI', 500, 1);
INSERT INTO academic_setup_carrera (carrera_id, nombre_carrera, codigo_carrera, horas_totales_curricula, unidad_id) VALUES (2, 'Contabilidad y Finanzas', 'CF', 500, 1);
INSERT INTO academic_setup_carrera (carrera_id, nombre_carrera, codigo_carrera, horas_totales_curricula, unidad_id) VALUES (3, 'Administracion de Empresas', 'AE', 500, 1);
INSERT INTO academic_setup_carrera (carrera_id, nombre_carrera, codigo_carrera, horas_totales_curricula, unidad_id) VALUES (4, 'Administración de Empresas instituto', 'AEI', 450, 2);
INSERT INTO academic_setup_carrera (carrera_id, nombre_carrera, codigo_carrera, horas_totales_curricula, unidad_id) VALUES (5, 'Contabilidad', 'CI', 300, 2);
INSERT INTO academic_setup_carrera (carrera_id, nombre_carrera, codigo_carrera, horas_totales_curricula, unidad_id) VALUES (6, 'Enfermería Técnica', 'ETI', 450, 2);

-- ============================================
-- 7. academic_setup_ciclo
-- ============================================
-- Nota: Hay 48 ciclos, incluyo algunos ejemplos

INSERT INTO academic_setup_ciclo (ciclo_id, nombre_ciclo, orden, carrera_id) VALUES (1, 'ciclo 1', 1, 1);
INSERT INTO academic_setup_ciclo (ciclo_id, nombre_ciclo, orden, carrera_id) VALUES (2, 'ciclo 2', 2, 1);
-- ... (continuar con los 46 restantes)

-- ============================================
-- 9. academic_setup_periodoacademico
-- ============================================

INSERT INTO academic_setup_periodoacademico (periodo_id, nombre_periodo, fecha_inicio, fecha_fin, activo) VALUES (1, '2025-A', '2025-06-01', '2025-09-30', TRUE);
INSERT INTO academic_setup_periodoacademico (periodo_id, nombre_periodo, fecha_inicio, fecha_fin, activo) VALUES (2, '2025-B', '2025-10-01', '2026-01-31', TRUE);
INSERT INTO academic_setup_periodoacademico (periodo_id, nombre_periodo, fecha_inicio, fecha_fin, activo) VALUES (3, '2025-C', '2025-07-05', '2025-07-31', TRUE);

-- ============================================
-- 10. academic_setup_materias
-- ============================================
-- Nota: Hay 189 materias, incluyo algunas ejemplos clave

INSERT INTO academic_setup_materias (materia_id, codigo_materia, nombre_materia, descripcion, horas_academicas_teoricas, horas_academicas_practicas, horas_academicas_laboratorio, estado, requiere_tipo_espacio_especifico_id) VALUES (1, 'ADE-001', 'Matemática para los Negocios', NULL, 1, 1, 1, TRUE, 2);
INSERT INTO academic_setup_materias (materia_id, codigo_materia, nombre_materia, descripcion, horas_academicas_teoricas, horas_academicas_practicas, horas_academicas_laboratorio, estado, requiere_tipo_espacio_especifico_id) VALUES (2, 'ADE-004', 'Introducción a la Contabilidad', NULL, 1, 1, 1, TRUE, 2);
-- ... (continuar con las 187 restantes)

-- ============================================
-- 13. users_docentes
-- ============================================
-- Nota: Hay 117 docentes, incluyo algunos ejemplos

INSERT INTO users_docentes (docente_id, codigo_docente, nombres, apellidos, dni, email, telefono, tipo_contrato, max_horas_semanales, unidad_principal_id, usuario_id) VALUES (1, 'U1', 'ERICK', 'QUISPE', '12345687', 'erick@gmail.com', NULL, 'TC', 40, 1, 2);
INSERT INTO users_docentes (docente_id, codigo_docente, nombres, apellidos, dni, email, telefono, tipo_contrato, max_horas_semanales, unidad_principal_id, usuario_id) VALUES (2, 'U2', 'Andre', 'Mendez', '78945621', 'guillermo@gmail.com', NULL, 'TC', 40, 1, 3);
-- ... (continuar con los 115 restantes)

-- ============================================
-- 15. academic_setup_materiaespecialidadesrequeridas
-- ============================================
-- Nota: Hay 141 relaciones, incluyo algunas ejemplos

INSERT INTO academic_setup_materiaespecialidadesrequeridas (id, especialidad_id, materia_id) VALUES (200, 5, 124);
INSERT INTO academic_setup_materiaespecialidadesrequeridas (id, especialidad_id, materia_id) VALUES (201, 10, 54);
-- ... (continuar con las 139 restantes)

-- ============================================
-- 17. scheduling_bloqueshorariosdefinicion
-- ============================================
-- Nota: Hay 138 bloques, incluyo algunos ejemplos

INSERT INTO scheduling_bloqueshorariosdefinicion (bloque_def_id, nombre_bloque, hora_inicio, hora_fin, turno, dia_semana) VALUES (1, 'mañana', '06:00:00', '06:45:00', 'M', 1);
INSERT INTO scheduling_bloqueshorariosdefinicion (bloque_def_id, nombre_bloque, hora_inicio, hora_fin, turno, dia_semana) VALUES (2, 'mañana', '06:00:00', '06:45:00', 'M', 2);
-- ... (continuar con los 136 restantes)

-- ============================================
-- 19. scheduling_grupos_materias
-- ============================================
-- Nota: Hay 162 relaciones, incluyo algunas ejemplos

INSERT INTO scheduling_grupos_materias (id, grupos_id, materias_id) VALUES (159, 1, 134);
INSERT INTO scheduling_grupos_materias (id, grupos_id, materias_id) VALUES (8, 2, 7);
-- ... (continuar con las 160 restantes)

-- ============================================
-- 21. scheduling_configuracionrestricciones
-- ============================================

INSERT INTO scheduling_configuracionrestricciones (restriccion_id, codigo_restriccion, descripcion, tipo_aplicacion, entidad_id_1, entidad_id_2, valor_parametro, esta_activa, periodo_aplicable_id) VALUES (4, 'MAX_HORAS_DIA_GRUPO', 'Maximo de horas asignados a cada grupo', 'GLOBAL', NULL, NULL, '5', TRUE, 3);

-- ============================================
-- NOTA IMPORTANTE
-- ============================================
-- Este script contiene solo ejemplos de cada tabla.
-- Para completar la migración, necesito que me proporciones:
-- 1. Los datos completos de las tablas que faltan (seccion, espaciosfisicos, roles, carreramaterias, docenteespecialidades, grupos, disponibilidaddocentes)
-- 2. O ejecuta el script completo en PostgreSQL y exporta todo como CSV
-- 3. HorariosAsignados NO está incluido según tu solicitud

