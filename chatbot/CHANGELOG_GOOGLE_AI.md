# 🤖 Integración de Google AI en el Chatbot

## 📋 Resumen de Cambios

Se ha integrado Google AI (Gemini) como intermediario para el procesamiento de lenguaje natural del chatbot, permitiendo:

1. **Lenguaje completamente natural**: No requiere comandos específicos
2. **Personalización por usuario**: Respuestas adaptadas según el rol y nombre del usuario
3. **Mejor comprensión**: Google AI interpreta la intención del usuario de forma más precisa

## 🔧 Cambios Implementados

### 1. Nuevo Servicio: `google_ai_service.py`
- Servicio que usa Google Gemini para interpretar mensajes
- Genera intenciones estructuradas y mensajes personalizados
- Considera el contexto del usuario (nombre, rol)

### 2. Modificaciones en `nlp_service.py`
- Integración con Google AI
- Soporte para personalización por usuario
- Mantiene modo fallback con regex si Google AI no está disponible

### 3. Modificaciones en `views.py`
- Extracción de información del usuario (nombre, rol, perfil docente)
- Pasa contexto del usuario al servicio NLP
- Personaliza respuestas según el rol

### 4. Modificaciones en `query_service.py`
- Soporte para personalizar consultas según el rol
- Si un docente pregunta "mi horario", automáticamente usa su perfil

### 5. Configuración
- API Key agregada al `.env`
- Configuración en `settings.py`

## 🎯 Funcionalidades

### Personalización por Rol

#### Administrador
- Acceso completo a todas las consultas
- Puede comparar cualquier entidad
- Acceso a estadísticas completas

#### Coordinador Académico
- Puede consultar todo excepto información sensible de otros coordinadores
- Acceso a reportes y análisis

#### Docente
- Puede ver sus propios horarios con "mi horario" o "mis clases"
- Consultas básicas de aulas y disponibilidad
- Consultas sobre su carga horaria

### Ejemplos de Uso

**Antes (requería comandos específicos):**
```
"aulas disponibles lunes 8:00"
```

**Ahora (lenguaje natural):**
```
"Hola, ¿qué aulas están libres el lunes a las 8 de la mañana?"
"Necesito un aula para el lunes temprano"
"¿Dónde puedo dar clase el lunes a las 8?"
```

### Respuestas Personalizadas

El chatbot ahora responde usando el nombre del usuario:
```
Usuario: "Hola, ¿qué huecos tengo?"
Bot: "Hola Juan Pérez, revisando tus huecos disponibles..."
```

## 🔐 Configuración

La API Key de Google AI se configura en `.env`:
```env
GOOGLE_AI_API_KEY=AIzaSyD9I2GIGKPTce252a_ln79sQBQWI4L6EcI
```

## 📊 Flujo de Procesamiento

1. Usuario envía mensaje natural
2. Sistema extrae información del usuario (nombre, rol)
3. Google AI analiza el mensaje con contexto del usuario
4. Google AI genera:
   - Intención estructurada
   - Entidades extraídas
   - Mensaje personalizado
5. Sistema ejecuta consulta en base de datos
6. Respuesta personalizada al usuario

## ⚠️ Notas

- Si Google AI no está disponible, el sistema usa modo regex como fallback
- Los mensajes personalizados de Google AI se combinan con los datos de la consulta
- El sistema detecta automáticamente si el usuario es docente y personaliza "mi horario"

