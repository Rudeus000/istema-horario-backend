# Consultas Faltantes - Migración a Supabase

## 📊 Resumen del Estado Actual

### ✅ Datos COMPLETOS que ya tenemos:
- auth_user (121 usuarios) - **COMPLETO**
- academic_setup_unidadacademica (2 registros) - **COMPLETO**
- academic_setup_tiposespacio (4 registros) - **COMPLETO**
- academic_setup_especialidades (16 registros) - **COMPLETO**
- academic_setup_carrera (6 registros) - **COMPLETO**
- academic_setup_ciclo (48 registros) - **COMPLETO**
- academic_setup_periodoacademico (3 registros) - **COMPLETO**
- academic_setup_materias (144 registros) - **COMPLETO**
- users_docentes (117 registros) - **COMPLETO**
- academic_setup_materiaespecialidadesrequeridas (141 registros) - **COMPLETO**
- users_docenteespecialidades (337 registros) - **COMPLETO** ✅ NUEVO
- scheduling_grupos (35 registros) - **COMPLETO** ✅ NUEVO

### ⚠️ Datos INCOMPLETOS:
- scheduling_bloqueshorariosdefinicion - Se cortó en la salida anterior (necesitamos los 138 registros completos)

### ❌ Datos FALTANTES:

Necesitas ejecutar estas consultas en PostgreSQL y compartir los resultados:

---

## 🔍 Consultas a Ejecutar

### 1. Tipo de Unidad Académica
```sql
SELECT * FROM academic_setup_tipounidadacademica ORDER BY tipo_unidad_id;
```

### 2. Secciones
```sql
SELECT * FROM academic_setup_seccion ORDER BY seccion_id;
```

### 3. Espacios Físicos
```sql
SELECT * FROM academic_setup_espaciosfisicos ORDER BY espacio_id;
```

### 4. Roles
```sql
SELECT * FROM users_roles ORDER BY rol_id;
```

### 5. Carrera-Materias (relación)
```sql
SELECT * FROM academic_setup_carreramaterias;
```

### 6. Docente-Especialidades (relación) ✅ COMPLETO
```sql
SELECT * FROM users_docenteespecialidades;
```

### 7. Grupos ✅ COMPLETO
```sql
SELECT * FROM scheduling_grupos ORDER BY grupo_id;
```

### 8. Disponibilidad Docentes
```sql
SELECT * FROM scheduling_disponibilidaddocentes ORDER BY disponibilidad_id;
```

### 9. Bloques Horarios (COMPLETO - se cortó antes)
```sql
SELECT * FROM scheduling_bloqueshorariosdefinicion ORDER BY bloque_def_id;
```

### 10. Grupos-Materias (verificar)
```sql
SELECT * FROM scheduling_grupos_materias;
```

---

## 📝 Instrucciones

1. **Abre PostgreSQL** (psql o pgAdmin)
2. **Conecta** a tu base de datos local (`Sistemaponti`)
3. **Ejecuta cada consulta** una por una
4. **Copia TODO** el resultado de cada consulta
5. **Pega los resultados aquí** en el chat

---

## ⚠️ Importante

- **NO incluir** `scheduling_horariosasignados` (según tu solicitud)
- Si una consulta es muy larga, puedes:
  - Exportarla como CSV desde pgAdmin
  - O ejecutarla y copiar toda la salida
- Si ves caracteres raros (como `├í`, `├▒`), no te preocupes, los limpiaré automáticamente

---

## 🎯 Una vez que tengas todos los datos:

1. Te generaré el script SQL completo con todos los INSERTs
2. Podrás ejecutarlo en Supabase SQL Editor
3. ¡La migración estará completa!

