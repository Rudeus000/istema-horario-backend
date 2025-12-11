# Generar SQL Completo para Supabase

## 🚀 Opción 1: Usar el Script Automático (RECOMENDADO)

Ya tienes un script que genera el SQL completo automáticamente desde tu base de datos local:

```bash
# Asegúrate de estar en el directorio del backend
cd istema-horario-backend

# Activa tu entorno virtual (si usas uno)
# venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Ejecuta el script
python scripts/consultar_y_generar_sql.py
```

Este script:
- ✅ Conecta a tu base de datos local
- ✅ Consulta todas las tablas automáticamente
- ✅ Maneja problemas de encoding
- ✅ Genera el SQL completo con todos los INSERTs
- ✅ Excluye `scheduling_horariosasignados` (según tu solicitud)

El script generará un archivo: `inserts_supabase_YYYYMMDD_HHMMSS.sql`

---

## 📝 Opción 2: Ejecutar Consultas Manualmente

Si prefieres hacerlo manualmente, ejecuta estas consultas y comparte los resultados:

Ver archivo: `scripts/CONSULTAS_FALTANTES_FINAL.md`

---

## ✅ Después de Generar el SQL:

1. **Revisa el archivo SQL generado**
2. **Abre Supabase SQL Editor**
3. **Ejecuta primero**: `scripts/create_supabase_database.sql` (si aún no lo has hecho)
4. **Luego ejecuta**: El archivo SQL generado con los INSERTs
5. **Verifica**: Usa `scripts/verify_supabase_database.sql` para confirmar

---

## ⚠️ Nota Importante:

El script automático es más confiable porque:
- Maneja encoding automáticamente
- Respeta el orden de las foreign keys
- Genera SQL válido directamente
- Evita errores de copia/pega

