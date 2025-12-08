# 📋 Cómo Consultar y Compartir los Datos

## Paso 1: Ejecutar las Consultas

1. Abre tu cliente de PostgreSQL (pgAdmin, DBeaver, psql, etc.)
2. Conéctate a tu base de datos local: `Sistemaponti`
3. Abre el archivo `consultar_tablas_postgres.sql`
4. Ejecuta todas las consultas

## Paso 2: Exportar los Resultados

### Opción A: Exportar como CSV (Recomendado)
1. En pgAdmin: Click derecho en los resultados → "Exportar" → CSV
2. En DBeaver: Click derecho → "Export Data" → CSV
3. Guarda todos los CSVs en una carpeta

### Opción B: Copiar y Pegar
1. Selecciona todos los resultados de cada tabla
2. Copia (Ctrl+C)
3. Pega en un archivo de texto

### Opción C: Usar COPY TO (Más rápido)
Ejecuta estos comandos en psql o pgAdmin:

```sql
-- Exportar cada tabla a CSV
COPY (SELECT * FROM auth_user ORDER BY id) TO 'C:/ruta/temp/auth_user.csv' WITH CSV HEADER;
COPY (SELECT * FROM academic_setup_tipounidadacademica ORDER BY tipo_unidad_id) TO 'C:/ruta/temp/tipounidadacademica.csv' WITH CSV HEADER;
COPY (SELECT * FROM academic_setup_unidadacademica ORDER BY unidad_id) TO 'C:/ruta/temp/unidadacademica.csv' WITH CSV HEADER;
-- ... y así para todas las tablas
```

## Paso 3: Compartir los Datos

Puedes:
1. **Compartir los archivos CSV** - Te genero el script SQL automáticamente
2. **Pegar los datos aquí** - Te ayudo a formatearlos
3. **Compartir un dump SQL** - Si prefieres, puedo darte un script para hacer dump directo

## ⚠️ Importante

- **NO incluyas** la tabla `scheduling_horariosasignados`
- Asegúrate de que el encoding sea UTF-8
- Si hay errores de encoding, avísame y los limpiamos

## 📝 Tablas a Exportar

1. auth_user
2. academic_setup_tipounidadacademica
3. academic_setup_unidadacademica
4. academic_setup_tiposespacio
5. academic_setup_especialidades
6. academic_setup_carrera
7. academic_setup_ciclo
8. academic_setup_seccion
9. academic_setup_periodoacademico
10. academic_setup_materias
11. academic_setup_espaciosfisicos
12. users_roles
13. users_docentes
14. academic_setup_carreramaterias
15. academic_setup_materiaespecialidadesrequeridas
16. users_docenteespecialidades
17. scheduling_bloqueshorariosdefinicion
18. scheduling_grupos
19. scheduling_grupos_materias
20. scheduling_disponibilidaddocentes
21. scheduling_configuracionrestricciones
22. users_sesionesusuario

**NO incluir:** scheduling_horariosasignados

