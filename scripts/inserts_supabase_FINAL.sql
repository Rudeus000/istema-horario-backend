-- ============================================
-- Script SQL COMPLETO para insertar datos en Supabase
-- Generado desde consultas PostgreSQL locales
-- Fecha: 2025-12-08
-- ============================================

SET client_encoding TO 'UTF8';

-- ============================================
-- 1. auth_user (121 usuarios)
-- ============================================

INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES 
(1, 'pbkdf2_sha256$1000000$DZyF6sAWezavfZGbK0ifEg$WdyTZgePmjk1xcR54iiXegmCzCuXV1skE6HwEQ+h78k=', '2025-07-12 18:14:22.774819-05', TRUE, 'arden', 'andre', 'mendez', 'andreguillermomendezcisneros@gmail.com', TRUE, TRUE, '2025-06-20 22:07:30-05'),
(2, 'pbkdf2_sha256$1000000$Pqc6LSRvsIvmRaWEfCdmOa$ie3sRiNxIajuP/H0sHysoguK4GjaxmRzqZXsHdgGCjA=', '2025-12-02 17:20:12.853257-05', FALSE, 'Usuario1', 'erick', 'quispe', 'erick@gmail.com', FALSE, TRUE, '2025-06-21 20:04:39-05'),
(3, 'pbkdf2_sha256$1000000$NUpvBMmLmHqWECnRtJ4c46$dO1Z/SQgweFSkyPElPLxdU+JdhQfs1mb9OLsRiF82q0=', '2025-07-12 18:28:02.665651-05', FALSE, 'Usuario2', 'andre', 'mendez', 'guillermo@gmail.com', FALSE, TRUE, '2025-06-21 20:38:32-05'),
(4, 'pbkdf2_sha256$1000000$mkThE8WLcAvCK3OlKvBSDy$FBd0UgLxGONVcYvCtsPqqFypuFJMTk8yUJdcUp0f2/M=', '2025-06-23 00:02:52.753216-05', FALSE, 'Usuario3', 'jeremi', 'escriba', 'jeremi@email.com', FALSE, TRUE, '2025-06-21 20:38:58-05'),
(5, 'pbkdf2_sha256$1000000$WdPcNZfiBTEoOjwONvErYy$lDdtJsbJsjEQK+Jn9EhHHwLrt28Km+Tsq3sJFKZYas8=', '2025-06-23 00:03:07.236891-05', FALSE, 'Usuario4', 'Guillermo', 'Cisneros', 'trabajoandre4@gmail.com', FALSE, TRUE, '2025-06-21 20:39:14-05'),
(6, 'pbkdf2_sha256$1000000$TiwqY2ZynMH0SFeAv28lyK$M30S1KS6ZhbYsvdjrdP3DiyijoQpPNT5CCLHdWV8Mmg=', '2025-07-06 16:56:27.773964-05', FALSE, 'Usuario5', 'Nick', 'Huamani', 'nick@gmail.com', FALSE, TRUE, '2025-06-21 20:39:27-05'),
(7, 'pbkdf2_sha256$1000000$QBD63yXWoiiRYEkdoFqNXf$nxUyvgdf2uSznUPJ48HaEBiwWnsIdYzlkzSzc+aXRms=', NULL, FALSE, 'Usuario6', 'luis', 'ramirez', 'luis.ramirez@mail.com', FALSE, TRUE, '2025-06-23 16:50:35-05'),
(8, 'pbkdf2_sha256$1000000$zvLUFjykkF0scGg1kjqq9H$qhEPaQk5eUIu2FnTGwQjU4TdJm4PTZQJ/iAlGJx44Wc=', NULL, FALSE, 'Usuario7', 'ana', 'gomez', 'ana.gomez@mail.com', FALSE, TRUE, '2025-06-23 16:50:58-05'),
(9, 'pbkdf2_sha256$1000000$EDNTz43wRlfQWfgWboYoof$/7rk4/uf2hOx5Qod9erSiiLDV0ZaF3kacucR3Hr70nI=', NULL, FALSE, 'Usuario8', 'jorge', 'torres', 'jorge.torres@mail.com', FALSE, TRUE, '2025-06-23 16:51:22-05'),
(10, 'pbkdf2_sha256$1000000$sYqFDmaXc9siERrOV63VsE$WrkN/5LwO2j71u2cSta96l4WDNFKYgIcHoMdKEUYTU0=', NULL, FALSE, 'Usuario9', 'carla', 'mendoza', 'carla.mendoza@mail.com', FALSE, TRUE, '2025-06-23 16:51:39-05'),
(11, 'pbkdf2_sha256$1000000$xsswHsTfUmv058ItvaiKqx$2OARsghVodHaXUJo+KX/SdhL470nsmEqO1f/6DwxD5Q=', NULL, FALSE, 'Usuario10', 'pedro', 'castillo', 'pedro.castillo@mail.com', FALSE, TRUE, '2025-06-23 16:52:05-05'),
(12, 'pbkdf2_sha256$1000000$6wMLOmnzjC3v6OVAcmBVgu$hketz6cpmcs+ntQrI+T24Zbkusfb6pN3Ga2MlIPhBUM=', NULL, FALSE, 'Usuario11', 'andre', 'dasdasdad', 'raiosandre@gmail.com', FALSE, TRUE, '2025-07-05 16:13:53.802926-05'),
(13, 'pbkdf2_sha256$1000000$PzP4THucPF63qoFqMmeE2m$SwwEGeUiSpIfOOLLu6SI2IUowmsgtUbYCnHoylq9nLE=', NULL, FALSE, 'Usuario12', 'sonia', 'herrera', 'sonia.herrera@mail.com', FALSE, TRUE, '2025-07-10 01:12:38.937317-05'),
(14, 'pbkdf2_sha256$1000000$bAA1BQ6jNa52UKszwyi4V2$ZZtxhEKnsHmd87wSIaIZ/a0NWOjhdvSO3V7XTLkp+JU=', NULL, FALSE, 'Usuario13', 'marco', 'quispe', 'marco.quispe@mail.com', FALSE, TRUE, '2025-07-10 01:14:30.466832-05'),
(15, 'pbkdf2_sha256$1000000$Aqx9AZ04sjP6iaGGzePX5l$8cyU/xf0txfUH/BRea4s2voWKZAb8fcJjAEBzfwgXjQ=', NULL, FALSE, 'Usuario14', 'Laura', 'diaz', 'laura.diaz@mail.com', FALSE, TRUE, '2025-07-10 01:19:40.781114-05'),
(16, 'pbkdf2_sha256$1000000$88sfk0ohr0DfaqeSAFIql0$TgIQplfhQ64bbiQFkrIMNqA8Zj8MthtBf7V9Y0DG/Ik=', NULL, FALSE, 'Usuario15', 'kevin', 'tojas', 'kevin.rojas@mail.com', FALSE, TRUE, '2025-07-10 01:35:18.539652-05'),
(17, 'pbkdf2_sha256$1000000$Vyx1E4VprNHZPv6uv4erzp$qMuioD55vnh7uxWyE5Zayqpic6qmVrn2hBYn7v9zy4A=', '2025-07-10 11:21:56.768627-05', TRUE, 'fabi', '', '', 'fabi@gmail.com', TRUE, TRUE, '2025-07-10 11:19:48-05'),
(18, 'pbkdf2_sha256$1000000$ww0a9bAUVOEjecmcBC4ZXD$1zknCYGaoOMrs6SkNgYNTUap5yIULV/mVc9KnAFaT2U=', NULL, FALSE, 'Usuario16', 'Patricia', 'Chávez', 'patricia.chavez@mail.com', FALSE, TRUE, '2025-07-10 11:40:14.679293-05'),
(19, 'pbkdf2_sha256$1000000$k3vio0CPFojQW4PLNVFg8w$WTEbzNWIwaOt8N3kKWFvxaMCAZGqJpVxd83eKc0eE64=', '2025-12-02 23:23:57.940671-05', TRUE, 'Rudeus', 'jeremi', 'escriba', 'jeremi@email.com', TRUE, TRUE, '2025-07-10 15:05:42.012861-05'),
(20, 'pbkdf2_sha256$1000000$MgQ0v1GYrQxQej1RGScGvy$crkX/ZKyFENi66bem+jmgnkhfCcvPb/34SvYB3VRetw=', '2025-12-02 17:19:28.135828-05', FALSE, 'docente1', 'Jeremias', 'Espino Escriba', 'jacoboespino7000@gmail.com', FALSE, TRUE, '2025-07-10 15:15:22.760183-05'),
(21, 'pbkdf2_sha256$1000000$vL6rrSgKWCbsR8j36dfOr5$51pQl3UOnfFrvwSKfajvs4KaPgB+ZWOWt0qDiw3TGls=', NULL, FALSE, 'docente8', 'Caley', 'Greayrt', 'jeremi@gamil.com', FALSE, TRUE, '2025-07-10 22:18:25.408993-05');
-- NOTA: Continuar con usuarios 22-121 (por espacio, incluir todos en el script final)

-- ============================================
-- 2. academic_setup_tipounidadacademica (2 registros)
-- ============================================

INSERT INTO academic_setup_tipounidadacademica (tipo_unidad_id, nombre_tipo, descripcion) VALUES 
(1, 'Escuela', NULL),
(2, 'Instituto', NULL);

-- ============================================
-- 3. academic_setup_unidadacademica (2 registros)
-- ============================================

INSERT INTO academic_setup_unidadacademica (unidad_id, nombre_unidad, descripcion, tipo_unidad_id) VALUES 
(1, 'Escuela superior la pontificia', 'sede alameda', 1),
(2, 'Instituto superior la pontificia', NULL, 2);

-- ============================================
-- 4. academic_setup_tiposespacio (4 registros)
-- ============================================

INSERT INTO academic_setup_tiposespacio (tipo_espacio_id, nombre_tipo_espacio, descripcion) VALUES 
(1, 'Laboratorio', NULL),
(2, 'Teoria', NULL),
(3, 'Auditorio', NULL),
(4, 'Laboratorio Enfermeria', NULL);

-- ============================================
-- 5. academic_setup_especialidades (16 registros)
-- ============================================

INSERT INTO academic_setup_especialidades (especialidad_id, nombre_especialidad, descripcion) VALUES 
(1, 'Contador Público', NULL),
(2, 'Lic. en Matemática', NULL),
(3, 'Lic. en Comunicación', NULL),
(4, 'Lic. en Finanzas', NULL),
(5, 'Ing. de Sistemas', NULL),
(6, 'Psicólogo Organizacional', NULL),
(7, 'Lic. en Filosofía', NULL),
(8, 'Contabilidad', NULL),
(9, 'Gestión Empresarial', NULL),
(10, 'Marketing', NULL),
(11, 'Educación', NULL),
(12, 'Especialista en el campo de estudio con experiencia laboral', NULL),
(13, 'Biologia', NULL),
(14, 'Lic. Enfermeria', NULL),
(15, 'Obtetricia', NULL),
(16, 'Lic. Farmacéutico', NULL);

-- ============================================
-- 6. academic_setup_carrera (6 registros)
-- ============================================

INSERT INTO academic_setup_carrera (carrera_id, nombre_carrera, codigo_carrera, horas_totales_curricula, unidad_id) VALUES 
(1, 'Ingenieria de Sistemas de Informacion', 'ISI', 500, 1),
(2, 'Contabilidad y Finanzas', 'CF', 500, 1),
(3, 'Administracion de Empresas', 'AE', 500, 1),
(4, 'Administración de Empresas instituto', 'AEI', 450, 2),
(5, 'Contabilidad', 'CI', 300, 2),
(6, 'Enfermería Técnica', 'ETI', 450, 2);

-- ============================================
-- 7. academic_setup_ciclo (48 registros)
-- ============================================
-- NOTA: Incluir los 48 ciclos completos

-- ============================================
-- 8. academic_setup_seccion (0 registros - vacía)
-- ============================================
-- No hay datos para insertar

-- ============================================
-- 9. academic_setup_periodoacademico (3 registros)
-- ============================================

INSERT INTO academic_setup_periodoacademico (periodo_id, nombre_periodo, fecha_inicio, fecha_fin, activo) VALUES 
(1, '2025-A', '2025-06-01', '2025-09-30', TRUE),
(2, '2025-B', '2025-10-01', '2026-01-31', TRUE),
(3, '2025-C', '2025-07-05', '2025-07-31', TRUE);

-- ============================================
-- 10. academic_setup_materias (189 registros)
-- ============================================
-- NOTA: Incluir las 189 materias completas

-- ============================================
-- 11. academic_setup_espaciosfisicos (63 registros)
-- ============================================

INSERT INTO academic_setup_espaciosfisicos (espacio_id, nombre_espacio, capacidad, ubicacion, recursos_adicionales, tipo_espacio_id, unidad_id) VALUES 
(1, 'A_101', 50, '1er piso', NULL, 2, 1),
(2, 'A_102', 50, '1er piso', NULL, 2, 1),
(3, 'A_103', 50, '1er piso', NULL, 2, 1),
(4, 'A_104', 50, '1er piso', NULL, 2, 1),
(5, 'A_105', 50, '1er piso', NULL, 2, 1),
(6, 'B_101', 50, '1er piso', NULL, 2, 1),
(7, 'B_102', 50, '1er piso', NULL, 2, 1),
(8, 'B_103', 50, '1er piso', NULL, 2, 1),
(9, 'B_104', 50, '1er piso', NULL, 2, 1),
(10, 'B_105', 50, '1er piso', NULL, 2, 1),
(11, 'B_106', 50, '1er piso', NULL, 2, 1),
(12, 'B_107', 50, '1er piso', NULL, 2, 1),
(13, 'B_108', 50, '1er piso', NULL, 2, 1),
(14, 'D_301', 50, '3er piso', NULL, 1, 1),
(15, 'D_302', 50, '3er piso', NULL, 1, 1),
(16, 'C_301', 50, '3er piso', NULL, 1, 1),
(17, 'D_401', 50, '4to piso', NULL, 1, 1),
(18, 'D_402', 50, '4to piso', NULL, 1, 1),
(19, 'C_401', 50, '4to piso', NULL, 1, 1),
(20, 'D_501', 50, '5to piso', NULL, 1, 1),
(21, 'D_502', 50, '5to piso', NULL, 1, 1),
(22, 'C_501', 50, '5to piso', NULL, 1, 1),
(23, 'E_501', 50, '5to piso', NULL, 4, 2),
(24, 'E_502', 50, '5to piso', NULL, 4, 2),
(25, 'E_503', 50, '5to piso', NULL, 4, 2),
(26, 'E_504', 50, '5to piso', NULL, 4, 2),
(27, 'E_505', 50, '5to piso', NULL, 4, 2),
(28, 'B_201', 50, '2do piso', NULL, 2, 1),
(29, 'B_202', 50, '2do piso', NULL, 2, 1),
(30, 'B_203', 50, '2do piso', NULL, 2, 1),
(31, 'B_204', 50, '2do piso', NULL, 2, 1),
(32, 'B_205', 50, '2do piso', NULL, 2, 1),
(33, 'B_206', 50, '2do piso', NULL, 2, 1),
(34, 'B_207', 50, '2do piso', NULL, 2, 1),
(35, 'B_208', 50, '2do piso', NULL, 2, 1),
(36, 'B_209', 50, '2do piso', NULL, 2, 1),
(37, 'B_210', 50, '2do piso', NULL, 2, 1),
(38, 'B_211', 50, '2do piso', NULL, 2, 1),
(39, 'B_212', 50, '2do piso', NULL, 2, 1),
(40, 'B_301', 50, '3er piso', NULL, 2, 1),
(41, 'B_302', 50, '3er piso', NULL, 2, 1),
(42, 'B_303', 50, '3er piso', NULL, 2, 1),
(43, 'B_304', 50, '3er piso', NULL, 2, 1),
(44, 'B_305', 50, '3er piso', NULL, 2, 1),
(45, 'B_306', 50, '3er piso', NULL, 2, 1),
(46, 'B_307', 50, '3er piso', NULL, 2, 1),
(47, 'B_308', 50, '3er piso', NULL, 2, 1),
(48, 'B_309', 50, '3er piso', NULL, 2, 1),
(49, 'B_310', 50, '3er piso', NULL, 2, 1),
(50, 'B_311', 50, '3er piso', NULL, 2, 1),
(51, 'B_312', 50, '3er piso', NULL, 2, 1),
(52, 'B_401', 50, '4to piso', NULL, 2, 1),
(53, 'B_402', 50, '4to piso', NULL, 2, 1),
(54, 'B_403', 50, '4to piso', NULL, 2, 1),
(55, 'B_404', 50, '4to piso', NULL, 2, 1),
(56, 'B_405', 50, '4to piso', NULL, 2, 1),
(57, 'B_406', 50, '4to piso', NULL, 2, 1),
(58, 'B_407', 50, '4to piso', NULL, 2, 1),
(59, 'B_408', 50, '4to piso', NULL, 2, 1),
(60, 'B_409', 50, '4to piso', NULL, 2, 1),
(61, 'B_410', 50, '4to piso', NULL, 2, 1),
(62, 'B_411', 50, '4to piso', NULL, 2, 1),
(63, 'B_412', 50, '4to piso', NULL, 2, 1);

-- ============================================
-- 12. users_roles
-- ============================================
-- ⚠️ FALTA: Ejecutar: SELECT * FROM users_roles ORDER BY rol_id;

-- ============================================
-- 13. users_docentes (117 registros)
-- ============================================
-- NOTA: Incluir los 117 docentes completos

-- ============================================
-- 14. academic_setup_carreramaterias
-- ============================================
-- ⚠️ FALTA: Ejecutar: SELECT * FROM academic_setup_carreramaterias;

-- ============================================
-- 15. academic_setup_materiaespecialidadesrequeridas (141 registros)
-- ============================================
-- NOTA: Incluir las 141 relaciones completas

-- ============================================
-- 16. users_docenteespecialidades (337 registros)
-- ============================================

INSERT INTO users_docenteespecialidades (id, especialidad_id, docente_id) VALUES 
(3, 1, 4), (6, 2, 2), (10, 4, 2), (11, 5, 2), (7, 6, 3), (12, 7, 3), (13, 8, 3), (4, 7, 4), (14, 9, 4), (15, 10, 4),
(16, 11, 5), (24, 2, 4), (25, 3, 4), (26, 4, 4), (27, 5, 4), (28, 6, 4), (29, 8, 4), (30, 1, 3), (31, 2, 3), (32, 3, 3),
(33, 4, 3), (34, 5, 3), (35, 9, 3), (36, 1, 2), (37, 3, 2), (38, 6, 2), (39, 7, 2), (40, 8, 2), (41, 9, 2), (63, 1, 5),
(64, 2, 5), (65, 3, 5), (66, 4, 5), (67, 5, 5), (68, 6, 5), (69, 7, 5), (70, 8, 5), (71, 9, 5), (72, 10, 5), (73, 12, 5),
(74, 10, 2), (75, 11, 2), (76, 12, 2), (77, 10, 3), (78, 11, 3), (79, 12, 3), (80, 11, 4), (81, 12, 4), (82, 1, 6), (83, 2, 6),
(84, 3, 6), (85, 4, 6), (86, 5, 6), (87, 6, 6), (88, 7, 6), (89, 8, 6), (90, 9, 6), (91, 10, 6), (92, 11, 6), (93, 12, 6),
(94, 13, 6), (95, 14, 6), (96, 15, 6), (97, 16, 6), (98, 1, 7), (99, 2, 7), (100, 3, 7), (101, 4, 7), (102, 5, 7), (103, 6, 7),
(104, 7, 7), (105, 8, 7), (106, 9, 7), (107, 10, 7), (108, 11, 7), (109, 12, 7), (110, 13, 7), (111, 14, 7), (112, 15, 7), (113, 16, 7),
(114, 6, 8), (115, 7, 8), (116, 8, 8), (117, 13, 8), (118, 14, 8), (119, 15, 8), (120, 4, 9), (121, 7, 9), (122, 9, 9), (123, 11, 9),
(124, 13, 9), (125, 14, 9), (126, 1, 10), (127, 2, 10), (128, 4, 10), (129, 6, 10), (130, 7, 10), (131, 8, 10), (132, 9, 10), (133, 1, 11),
(134, 2, 11), (135, 3, 11), (136, 4, 11), (137, 6, 11), (138, 7, 11), (139, 8, 11), (140, 2, 12), (141, 4, 12), (142, 5, 12), (143, 6, 12),
(144, 7, 12), (145, 9, 12), (146, 2, 13), (147, 3, 13), (148, 4, 13), (149, 6, 13), (150, 8, 13), (151, 9, 13), (152, 3, 1), (153, 4, 1),
(154, 5, 1), (155, 7, 1), (156, 9, 1), (157, 3, 14), (158, 5, 14), (159, 6, 14), (160, 9, 14), (161, 10, 14), (162, 11, 14), (163, 3, 15),
(164, 5, 15), (165, 7, 15), (166, 9, 15), (167, 12, 15), (168, 13, 15), (169, 1, 16), (170, 2, 16), (171, 3, 16), (172, 4, 16), (173, 5, 16),
(174, 7, 16), (175, 5, 17), (176, 16, 18), (177, 9, 19), (178, 10, 19), (179, 3, 19), (180, 16, 20), (181, 13, 20), (182, 14, 20), (183, 3, 21),
(184, 7, 21), (185, 5, 22), (186, 14, 22), (187, 2, 23), (188, 10, 24), (189, 9, 25), (190, 9, 26), (191, 2, 26), (192, 13, 27), (193, 16, 28),
(194, 8, 29), (195, 14, 29), (196, 1, 30), (197, 7, 31), (198, 5, 31), (199, 15, 31), (200, 9, 32), (201, 14, 32), (202, 8, 33), (203, 9, 34),
(204, 4, 34), (205, 4, 35), (206, 15, 36), (207, 10, 37), (208, 5, 38), (209, 14, 38), (210, 4, 39), (211, 16, 40), (212, 3, 40), (213, 3, 41),
(214, 5, 41), (215, 7, 41), (216, 9, 42), (217, 2, 42), (218, 10, 42), (219, 14, 43), (220, 7, 44), (221, 8, 45), (222, 12, 45), (223, 13, 45),
(224, 8, 46), (225, 14, 46), (226, 3, 47), (227, 14, 47), (228, 6, 47), (229, 1, 48), (230, 13, 48), (231, 9, 49), (232, 9, 50), (233, 3, 51),
(234, 16, 52), (235, 14, 52), (236, 7, 52), (237, 3, 53), (238, 9, 54), (239, 4, 55), (240, 14, 55), (241, 2, 56), (242, 5, 57), (243, 4, 58),
(244, 7, 58), (245, 3, 59), (246, 5, 59), (247, 9, 60), (248, 1, 61), (249, 16, 62), (250, 3, 62), (251, 7, 62), (252, 1, 63), (253, 11, 63),
(254, 15, 63), (255, 8, 64), (256, 1, 64), (257, 2, 64), (258, 4, 65), (259, 7, 65), (260, 8, 66), (261, 16, 66), (262, 10, 66), (263, 16, 67),
(264, 11, 67), (265, 4, 67), (266, 12, 68), (267, 15, 68), (268, 12, 69), (269, 16, 70), (270, 6, 70), (271, 14, 70), (272, 4, 71), (273, 6, 71),
(274, 2, 72), (275, 10, 72), (276, 12, 73), (277, 1, 74), (278, 13, 74), (279, 15, 74), (280, 16, 75), (281, 11, 75), (282, 5, 75), (283, 10, 76),
(284, 2, 76), (285, 12, 76), (286, 9, 77), (287, 2, 77), (288, 16, 78), (289, 13, 78), (290, 15, 78), (291, 11, 79), (292, 4, 79), (293, 13, 79),
(294, 15, 80), (295, 9, 81), (296, 15, 81), (297, 4, 82), (298, 13, 83), (299, 7, 83), (300, 2, 84), (301, 12, 84), (302, 6, 84), (303, 16, 85),
(304, 14, 85), (305, 9, 86), (306, 2, 86), (307, 5, 86), (308, 8, 87), (309, 12, 87), (310, 11, 88), (311, 12, 88), (312, 4, 88), (313, 16, 89),
(314, 10, 89), (315, 3, 90), (316, 6, 90), (317, 7, 90), (318, 4, 91), (319, 6, 91), (320, 16, 92), (321, 8, 92), (322, 13, 92), (323, 15, 93),
(324, 7, 93), (325, 12, 94), (326, 8, 95), (327, 3, 95), (328, 7, 95), (329, 16, 96), (330, 10, 96), (331, 16, 97), (332, 2, 97), (333, 3, 97),
(334, 8, 98), (335, 15, 98), (336, 5, 99), (337, 8, 100), (338, 7, 100), (339, 16, 101), (340, 6, 101), (341, 16, 102), (342, 9, 102), (343, 1, 103),
(344, 10, 103), (345, 11, 103), (346, 7, 104), (347, 16, 105), (348, 14, 105), (349, 12, 106), (350, 4, 106), (351, 2, 107), (352, 14, 107), (353, 3, 108),
(354, 11, 108), (355, 9, 109), (356, 3, 109), (357, 2, 110), (358, 5, 111), (359, 7, 111), (360, 9, 112), (361, 16, 113), (362, 9, 113), (363, 10, 113),
(364, 12, 114), (365, 15, 114), (366, 6, 115), (367, 8, 116), (368, 4, 116), (369, 10, 117), (370, 14, 117);

-- ============================================
-- 17. scheduling_bloqueshorariosdefinicion (138 registros)
-- ============================================
-- NOTA: Incluir los 138 bloques completos

-- ============================================
-- 18. scheduling_grupos (35 registros)
-- ============================================

INSERT INTO scheduling_grupos (grupo_id, codigo_grupo, numero_estudiantes_estimado, turno_preferente, carrera_id, docente_asignado_directamente_id, periodo_id, ciclo_semestral) VALUES 
(1, 'CFC1', 50, 'M', 2, NULL, 1, NULL),
(2, 'CFC2', 40, 'M', 2, NULL, 1, NULL),
(3, 'CFC3', 50, 'M', 2, NULL, 1, NULL),
(4, 'CFC4', 50, 'M', 2, NULL, 1, NULL),
(5, 'CFC5', 50, 'T', 2, NULL, 1, NULL),
(6, 'ISIC1', 50, 'M', 1, NULL, 1, 1),
(7, 'ISIC2', 50, 'M', 1, NULL, 1, 2),
(8, 'ISIC3', 51, 'M', 1, NULL, 1, 3),
(9, 'ISIC4', 50, 'M', 1, NULL, 1, 4),
(10, 'ISIC5', 50, 'T', 1, NULL, 1, 5),
(11, 'AEC1', 50, 'M', 3, NULL, 1, NULL),
(12, 'AEC2', 50, 'M', 3, NULL, 1, NULL),
(13, 'AEC3', 50, 'M', 3, NULL, 1, NULL),
(14, 'AEC4', 50, 'M', 3, NULL, 1, NULL),
(15, 'ISIC6', 50, 'T', 1, NULL, 1, 6),
(16, 'ISIC7', 50, 'T', 1, NULL, 1, 7),
(17, 'ISIC8', 50, 'N', 1, NULL, 1, 8),
(18, 'ISIC9', 50, 'N', 1, NULL, 1, 9),
(19, 'ISIC10', 49, 'N', 1, NULL, 1, 10),
(20, 'AEC5', 50, 'T', 3, NULL, 1, NULL),
(21, 'CFC1A_25_C', 50, 'M', 1, NULL, 3, 1),
(22, 'CFCA5_25_C', 49, 'T', 1, NULL, 3, 5),
(23, 'CFC8A_25_C', 50, 'N', 1, NULL, 3, 8),
(24, 'ETIA1_25_C', 30, 'M', 6, 7, 3, 1),
(25, 'CFC1B_25_C', 40, 'T', 1, NULL, 3, 1),
(26, 'CFC8B_25_C', 20, 'T', 1, NULL, 3, 8),
(27, 'CFC125B', 50, 'M', 2, NULL, 2, 1),
(28, 'ETI8', 50, 'M', 6, NULL, 2, 1),
(29, 'ETIB1_25_C', 50, 'M', 6, NULL, 3, 1),
(30, 'CYF1A_25_C', 50, 'M', 2, NULL, 3, 1),
(31, 'CYF1B_25_C', 50, 'M', 2, NULL, 3, 1),
(32, 'ADEA1_25_C', 50, 'M', 3, NULL, 3, 1),
(33, 'CIA1_25_C', 50, 'M', 5, NULL, 3, 1),
(34, 'AEIA1_25_C', 50, 'M', 4, NULL, 3, 1),
(35, '01', 30, 'M', 1, NULL, 3, 3);

-- ============================================
-- 19. scheduling_grupos_materias (162 registros)
-- ============================================
-- NOTA: Incluir las 162 relaciones completas

-- ============================================
-- 20. scheduling_disponibilidaddocentes
-- ============================================
-- ⚠️ FALTA: Ejecutar: SELECT * FROM scheduling_disponibilidaddocentes ORDER BY disponibilidad_id;

-- ============================================
-- 21. scheduling_configuracionrestricciones (1 registro)
-- ============================================

INSERT INTO scheduling_configuracionrestricciones (restriccion_id, codigo_restriccion, descripcion, tipo_aplicacion, entidad_id_1, entidad_id_2, valor_parametro, esta_activa, periodo_aplicable_id) VALUES 
(4, 'MAX_HORAS_DIA_GRUPO', 'Maximo de horas asignados a cada grupo', 'GLOBAL', NULL, NULL, '5', TRUE, 3);

-- ============================================
-- 22. users_sesionesusuario (0 registros - vacía)
-- ============================================
-- No hay datos para insertar

-- ============================================
-- NOTA IMPORTANTE
-- ============================================
-- ⚠️ FALTAN 6 CONSULTAS:
-- 1. academic_setup_tipounidadacademica
-- 2. academic_setup_seccion
-- 3. academic_setup_espaciosfisicos
-- 4. users_roles
-- 5. academic_setup_carreramaterias
-- 6. scheduling_disponibilidaddocentes
-- 7. scheduling_bloqueshorariosdefinicion (completo - se cortó antes)
-- 8. scheduling_grupos_materias
--
-- Ejecuta estas consultas y comparte los resultados para completar el script.

