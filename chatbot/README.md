# 🤖 Chatbot del Sistema de Horarios

Chatbot inteligente que permite a los usuarios consultar información del sistema de horarios mediante lenguaje natural.

## 🎯 Características

- **Lenguaje Natural**: Los usuarios pueden hacer preguntas como hablan normalmente
- **Múltiples Consultas**: Soporta varios tipos de consultas sobre aulas, docentes, horarios, etc.
- **Integración con IA**: Opción de usar OpenAI para mejor comprensión (opcional)
- **API REST**: Endpoints RESTful para integrar con el frontend

## 📋 Tipos de Consultas Soportadas

### 🔍 Consultas Básicas
1. **Aulas Disponibles**: "¿Qué aulas están disponibles el lunes a las 8:00?"
2. **Docentes Disponibles**: "¿Qué docentes están libres los martes por la tarde?"
3. **Horarios de Docente**: "¿Qué horarios tiene el docente Juan Pérez?"
4. **Horarios de Aula**: "¿Qué clases hay en el aula A101?"
5. **Tipos de Aulas**: "¿Qué tipos de aulas hay?"
6. **Buscar Docente**: "Buscar docente llamado García"
7. **Buscar Aula**: "Buscar aula A101"

### 🕳️ Detección de Huecos
8. **Huecos en Horarios**: "¿Qué huecos hay el lunes?"
9. **Huecos de Docente**: "¿Qué huecos tiene el docente Juan Pérez?"
10. **Huecos de Aula**: "¿Qué huecos tiene el aula A101?"
11. **Huecos de Grupo**: "¿Qué huecos tiene el grupo GR001?"

### 📊 Comparaciones
12. **Comparar Docentes**: "Compara docentes Juan y María"
13. **Comparar Aulas**: "Compara aulas A101 y A102"
14. **Carga de Docente**: "¿Cuántas clases tiene el docente Juan?"
15. **Carga de Aula**: "¿Cuántas clases se dan en el aula A101?"

### 📈 Estadísticas y Análisis
16. **Estadísticas del Período**: "Dame estadísticas del período"
17. **Análisis Completo**: "Análisis completo"
18. **Conflictos**: "¿Hay conflictos de horarios?"

### 🎓 Búsquedas Académicas
19. **Buscar Materia**: "Buscar materia Matemáticas"
20. **Buscar Carrera**: "Buscar carrera Ingeniería"
21. **Materias de Carrera**: "¿Qué materias tiene la carrera de Ingeniería?"
22. **Grupos de Carrera**: "¿Qué grupos tiene la carrera de Ingeniería?"
23. **Horarios de Grupo**: "¿Qué horarios tiene el grupo GR001?"

## 🚀 Uso

### Endpoint Principal

**POST** `/api/chatbot/chat/`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
    "message": "¿Qué aulas están disponibles el lunes a las 8:00?",
    "conversation_id": "optional-id"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Encontré 5 aula(s) disponible(s) para el Lunes a las 08:00.",
    "data": [
        {
            "id": 1,
            "nombre": "A101",
            "tipo": "Aula",
            "capacidad": 40,
            "ubicacion": "Edificio A"
        },
        ...
    ],
    "query_type": "aulas_disponibles",
    "confidence": 0.8,
    "count": 5
}
```

### Endpoint de Ayuda

**GET** `/api/chatbot/help/`

Retorna ejemplos de preguntas que puedes hacer.

## 🔧 Configuración

### Modo Básico (Regex)

Por defecto, el chatbot usa patrones regex para interpretar las preguntas. No requiere configuración adicional.

### Modo IA (OpenAI) - Opcional

Para usar OpenAI para mejor comprensión:

1. Instalar dependencias:
```bash
pip install openai
```

2. Agregar API key en `.env`:
```env
OPENAI_API_KEY=tu-api-key-aqui
```

3. Modificar `chatbot/services/nlp_service.py`:
```python
nlp_service = NLPService(use_ai=True, openai_api_key=os.getenv('OPENAI_API_KEY'))
```

## 📁 Estructura

```
chatbot/
├── services/
│   ├── nlp_service.py      # Procesamiento de lenguaje natural
│   └── query_service.py    # Consultas a la base de datos
├── views.py                # Vistas API
├── serializers.py          # Serializers DRF
├── urls.py                 # URLs
└── README.md
```

## 🔍 Ejemplos de Preguntas

### Consultas Básicas
- "¿Qué aulas están disponibles el lunes a las 8:00?"
- "¿Qué docentes están libres los martes por la tarde?"
- "¿Qué horarios tiene el docente Juan Pérez?"
- "¿Qué clases hay en el aula A101?"
- "¿Qué tipos de aulas hay?"
- "Buscar docente llamado García"

### Huecos y Disponibilidad
- "¿Qué huecos hay el lunes?"
- "¿Qué huecos tiene el docente Juan Pérez?"
- "¿Qué huecos tiene el aula A101?"
- "¿Dónde hay espacios libres?"

### Comparaciones y Estadísticas
- "Compara docentes Juan y María"
- "¿Cuántas clases tiene el docente Juan?"
- "Dame estadísticas del período"
- "Análisis completo"

### Búsquedas Académicas
- "Buscar materia Matemáticas"
- "¿Qué materias tiene la carrera de Ingeniería?"
- "¿Qué horarios tiene el grupo GR001?"

### Otros
- "¿Hay conflictos de horarios?"
- "Hola"
- "Ayuda"

## 🛠️ Desarrollo

### Agregar Nueva Intención

1. Agregar tipo en `nlp_service.py`:
```python
class IntentType(Enum):
    NUEVA_INTENCION = "nueva_intencion"
```

2. Agregar patrones en `INTENT_PATTERNS`:
```python
IntentType.NUEVA_INTENCION: [
    r'patrón\s+de\s+búsqueda',
]
```

3. Implementar método en `query_service.py`:
```python
def _query_nueva_intencion(self, entities: Dict) -> Dict:
    # Lógica de consulta
    return {
        'success': True,
        'data': [...],
        'message': 'Respuesta...',
        'query_type': 'nueva_intencion'
    }
```

4. Agregar caso en `execute_query()`:
```python
elif intent == IntentType.NUEVA_INTENCION:
    return self._query_nueva_intencion(entities)
```

## 📝 Notas

- El chatbot requiere autenticación JWT
- Las consultas usan el período académico activo por defecto
- Los resultados están limitados a 20 items por consulta
- El sistema funciona sin IA, pero la IA mejora la precisión

