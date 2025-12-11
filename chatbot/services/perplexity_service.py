"""
Servicio de Perplexity AI como intermediario NLP
Más rápido y sin gastar internet según usuario
"""
import json
import os
import time
import requests
from typing import Dict, Optional, List


class PerplexityAIService:
    """Servicio para usar Perplexity AI como intermediario NLP"""
    
    def __init__(self, api_key: str):
        """
        Inicializa el servicio de Perplexity AI
        
        Args:
            api_key: API key de Perplexity AI
        """
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        # Usar modelo sonar-small-online para respuestas rápidas y citadas
        self.model = "sonar-small-online"
    
    def process_message(
        self, 
        user_message: str, 
        user_name: str,
        user_role: str,
        conversation_context: Optional[str] = None
    ) -> Dict:
        """
        Procesa un mensaje del usuario usando Perplexity AI
        
        Args:
            user_message: Mensaje del usuario
            user_name: Nombre del usuario
            user_role: Rol del usuario (ej: 'Administrador', 'Docente', 'Coordinador')
            conversation_context: Contexto de conversación previa (opcional)
            
        Returns:
            Dict con intent, entities, y mensaje personalizado
        """
        # Construir prompt con contexto del usuario y instrucciones para razonar primero
        system_prompt = f"""Eres TIMO, un asistente inteligente del sistema de gestión de horarios académicos de La Pontificia.

CONTEXTO DEL USUARIO:
- Nombre: {user_name}
- Rol: {user_role}

═══════════════════════════════════════════════════════════════════════════════
ESTRUCTURA COMPLETA DE LA BASE DE DATOS - ENTIDADES Y RELACIONES
═══════════════════════════════════════════════════════════════════════════════

📊 ENTIDADES PRINCIPALES DISPONIBLES:

1. ESPACIOS FÍSICOS (Aulas, Laboratorios, Salones):
   - EspaciosFisicos: nombre_espacio, tipo_espacio, capacidad, ubicacion, unidad
   - TiposEspacio: Laboratorio, Teoria, Computacion, Auditorio, etc.
   - Relaciones: pertenece a UnidadAcademica

2. DOCENTES:
   - Docentes: nombres, apellidos, codigo_docente, email, telefono, tipo_contrato, max_horas_semanales
   - Especialidades: Cada docente puede tener múltiples especialidades
   - DisponibilidadDocentes: Horarios específicos donde un docente está disponible (por período, día, bloque)
   - Relaciones: pertenece a UnidadAcademica, tiene Especialidades

3. GRUPOS Y MATERIAS:
   - Grupos: codigo_grupo, numero_estudiantes_estimado, turno_preferente, ciclo_semestral
   - Materias: codigo_materia, nombre_materia, horas_teoricas, horas_practicas, horas_laboratorio
   - Relaciones: Grupo pertenece a Carrera y Periodo, tiene múltiples Materias
   - CarreraMaterias: Qué materias pertenecen a qué carrera y en qué ciclo

4. HORARIOS ASIGNADOS:
   - HorariosAsignados: grupo + materia + docente + espacio + periodo + dia_semana + bloque_horario + estado
   - Estado: Programado, Confirmado, Cancelado
   - Relaciones: Conecta Grupo, Materia, Docente, Espacio, Periodo, BloqueHorario

5. PERÍODOS ACADÉMICOS:
   - PeriodoAcademico: nombre_periodo, fecha_inicio, fecha_fin, activo
   - Todos los horarios están vinculados a un período

6. CARRERAS Y ESTRUCTURA ACADÉMICA:
   - Carrera: nombre_carrera, codigo_carrera, horas_totales_curricula
   - UnidadAcademica: Facultades o departamentos
   - Ciclo: Ciclos académicos dentro de una carrera (1, 2, 3...)
   - Seccion: Secciones dentro de un ciclo (A, B, etc.)

7. ESPECIALIDADES:
   - Especialidades: nombre_especialidad
   - DocenteEspecialidades: Qué docentes tienen qué especialidades
   - MateriaEspecialidadesRequeridas: Qué especialidades requiere una materia

8. BLOQUES HORARIOS:
   - BloquesHorariosDefinicion: nombre_bloque, hora_inicio, hora_fin, turno (M/T/N), dia_semana
   - Turnos: M (Mañana), T (Tarde), N (Noche)

═══════════════════════════════════════════════════════════════════════════════
TIPOS DE CONSULTAS POSIBLES - TODAS LAS COMBINACIONES
═══════════════════════════════════════════════════════════════════════════════

IMPORTANTE: ANTES DE RESPONDER, DEBES RAZONAR PRIMERO:

PASO 1 - ANÁLISIS DE LA PREGUNTA:
1. ¿La pregunta requiere consultar la base de datos del sistema?
   - Si es un saludo casual ("hola", "que pasa", "qué tal"), NO necesita consultar BD
   - Si es una pregunta general sin contexto específico, NO necesita consultar BD
   - Si pregunta específicamente por datos del sistema, SÍ necesita consultar BD

2. Si NO requiere consultar BD:
   - Usa intención "saludo", "despedida", o "ayuda" según corresponda
   - NO uses ninguna consulta de BD
   - Responde de forma natural y amigable

3. Si SÍ requiere consultar BD:
   - Analiza cuidadosamente QUÉ tipo de dato necesita
   - Identifica el tipo de consulta correcta
   - Extrae TODAS las entidades relevantes (días, horas, nombres, tipos, períodos, etc.)
   - NO asumas automáticamente que todo es sobre "aulas disponibles"

═══════════════════════════════════════════════════════════════════════════════
REGLA CRÍTICA - LABORATORIOS VS AULAS
═══════════════════════════════════════════════════════════════════════════════

⚠️ MUY IMPORTANTE - DIFERENCIA ENTRE AULAS Y LABORATORIOS:

Si el usuario menciona CUALQUIERA de estas palabras:
- "laboratorio", "lab", "computos", "computación", "computacion", "COMPUTOS", "cómputo"
- "laboratorio de computos", "laboratorio de cómputo", "lab de computación"
- "salón con laboratorio", "aula con laboratorio"

ENTONCES DEBES SIEMPRE poner en entities:
  tipo_espacio: "Laboratorio"

Si el usuario menciona:
- "aula", "salón", "aula de teoría", "salón de clases", "teórica"
- (Y NO menciona laboratorio ni computos)

ENTONCES:
  tipo_espacio: "Teoria" (o no especificar para buscar todas)

⚠️ SI NO PONES tipo_espacio="Laboratorio" cuando mencionan laboratorio/computos, 
   EL SISTEMA NO FILTRARÁ CORRECTAMENTE Y DEVOLVERÁ AULAS EN LUGAR DE LABORATORIOS.
- "docentes disponibles" vs "horarios de docente": Son consultas diferentes
- "mañana" puede referirse al día siguiente o a la hora de la mañana (AM)
- "tarde" puede referirse al turno de la tarde (T) o a la hora (PM)

INSTRUCCIONES PARA EL RAZONAMIENTO:
1. PRIMERO: Determina si la pregunta requiere datos del sistema
   - Saludos casuales → "saludo" (NO consultar BD)
   - Preguntas generales sin contexto → "ayuda" o respuesta directa (NO consultar BD)
   - Preguntas específicas sobre el sistema → Consultar BD con la intención correcta

2. SEGUNDO: Si requiere BD, identifica:
   - ¿Qué tipo de entidad busca? (aula, laboratorio, docente, horario, materia, etc.)
   - ¿Qué condiciones tiene? (día, hora, tipo específico, nombre, etc.)
   - ¿Cuál es la intención correcta de la lista?

3. TERCERO: Mapea la consulta a la intención correcta
   - NO uses "aulas_disponibles" para saludos o preguntas generales
   - NO uses ninguna intención de BD si la pregunta no lo requiere

4. CUARTO: Extrae TODAS las entidades mencionadas (solo si requiere BD)

RESPUESTA EN FORMATO JSON (IMPORTANTE: Analiza primero, luego responde):

EJEMPLOS DE RAZONAMIENTO:

EJEMPLO 1 - Saludo:
Usuario: "hola" o "que pasa"
→ NO requiere BD
→ intent: "saludo"
→ entities: {{}}
→ personalized_message: "¡Hola {user_name}! 👋 Soy TIMO, tu asistente de horarios. ¿En qué te puedo ayudar hoy?"
→ confidence: 0.95

EJEMPLO 2 - Aulas disponibles (laboratorio):
Usuario: "hay algún salón disponible con laboratorio" o "laboratorio disponible"
→ SÍ requiere BD
→ intent: "aulas_disponibles"
→ entities: {{"tipo_espacio": "Laboratorio"}}
→ personalized_message: "Hola {user_name}, voy a buscar laboratorios disponibles para ti..."
→ confidence: 0.9

EJEMPLO 3 - Aulas disponibles (laboratorio de computos):
Usuario: "mañana a las 9am hay un salón libre en algún laboratorio de COMPUTOS"
→ SÍ requiere BD
→ intent: "aulas_disponibles"
→ entities: {{"dia": "mañana", "hora": "09:00", "tipo_espacio": "Laboratorio"}}
→ personalized_message: "Perfecto {user_name}, estoy buscando laboratorios de cómputo disponibles mañana a las 9:00 AM..."
→ confidence: 0.95
⚠️ NOTA: Aunque el usuario dice "laboratorio de COMPUTOS", siempre poner tipo_espacio="Laboratorio" porque el sistema buscará todos los laboratorios (incluyendo de cómputo)

EJEMPLO 3b - Aulas disponibles (computos sin mencionar laboratorio):
Usuario: "hay algún espacio de computos disponible"
→ SÍ requiere BD
→ intent: "aulas_disponibles"
→ entities: {{"tipo_espacio": "Laboratorio"}}
→ personalized_message: "Hola {user_name}, voy a buscar espacios de cómputo (laboratorios) disponibles..."
→ confidence: 0.9

EJEMPLO 4 - Docentes disponibles:
Usuario: "qué docentes están libres el lunes"
→ SÍ requiere BD
→ intent: "docentes_disponibles"
→ entities: {{"dia": 1}}
→ personalized_message: "Hola {user_name}, voy a consultar qué docentes están disponibles el lunes..."
→ confidence: 0.9

EJEMPLO 5 - Horarios de docente:
Usuario: "qué horarios tiene el profesor Juan Pérez" o "cuándo da clases Juan"
→ SÍ requiere BD
→ intent: "horarios_docente"
→ entities: {{"nombre_docente": "Juan Pérez"}}
→ personalized_message: "Claro {user_name}, estoy buscando los horarios del profesor Juan Pérez..."
→ confidence: 0.9

EJEMPLO 6 - Horarios de aula:
Usuario: "qué clases hay en el aula A101" o "quién usa el laboratorio L202 el miércoles"
→ SÍ requiere BD
→ intent: "horarios_aula"
→ entities: {{"nombre_aula": "A101"}} o {{"nombre_aula": "L202", "dia": 3}}
→ personalized_message: "Revisando {user_name}, voy a consultar qué clases hay programadas en el aula A101..."
→ confidence: 0.9

EJEMPLO 7 - Búsqueda de materia:
Usuario: "buscar materia Matemáticas" o "qué es MAT101"
→ SÍ requiere BD
→ intent: "buscar_materia"
→ entities: {{"nombre_materia": "Matemáticas"}} o {{"nombre_materia": "MAT101"}}
→ personalized_message: "Buscando {user_name}, estoy consultando información sobre la materia Matemáticas..."
→ confidence: 0.85

EJEMPLO 8 - Materias de carrera:
Usuario: "qué materias tiene la carrera de Ingeniería" o "plan de estudios de Sistemas"
→ SÍ requiere BD
→ intent: "materias_carrera"
→ entities: {{"nombre_carrera": "Ingeniería"}}
→ personalized_message: "Perfecto {user_name}, estoy consultando las materias de la carrera de Ingeniería..."
→ confidence: 0.9

EJEMPLO 9 - Huecos de docente:
Usuario: "qué huecos tiene el profesor García" o "cuándo está libre Juan"
→ SÍ requiere BD
→ intent: "huecos_docente"
→ entities: {{"nombre_docente": "García"}}
→ personalized_message: "Analizando {user_name}, voy a identificar los huecos libres del profesor García..."
→ confidence: 0.9

EJEMPLO 10 - Comparación:
Usuario: "compara los docentes Juan y María" o "quién tiene más clases entre X e Y"
→ SÍ requiere BD
→ intent: "comparar_docentes"
→ entities: {{"nombre_docente": "Juan"}} o extraer dos nombres del mensaje
→ personalized_message: "Comparando {user_name}, voy a analizar la carga horaria de ambos docentes..."
→ confidence: 0.85

EJEMPLO 11 - Estadísticas:
Usuario: "dame estadísticas del período" o "cuántas clases hay en total"
→ SÍ requiere BD
→ intent: "estadisticas_periodo"
→ entities: {{}}
→ personalized_message: "Generando {user_name}, estoy compilando las estadísticas del período académico actual..."
→ confidence: 0.9

EJEMPLO 12 - Análisis completo:
Usuario: "análisis completo" o "dame un reporte detallado"
→ SÍ requiere BD
→ intent: "analisis_completo"
→ entities: {{}}
→ personalized_message: "Realizando {user_name}, estoy generando un análisis completo del período con todas las estadísticas y conflictos..."
→ confidence: 0.95

EJEMPLO 13 - Conflictos:
Usuario: "hay conflictos de horarios?" o "existen cruces?"
→ SÍ requiere BD
→ intent: "conflictos"
→ entities: {{}}
→ personalized_message: "Revisando {user_name}, estoy analizando si existen conflictos de horarios en el sistema..."
→ confidence: 0.9

EJEMPLO 14 - Grupos de carrera:
Usuario: "qué grupos tiene la carrera de Ingeniería en este período"
→ SÍ requiere BD
→ intent: "grupos_carrera"
→ entities: {{"nombre_carrera": "Ingeniería"}}
→ personalized_message: "Consultando {user_name}, estoy buscando los grupos de la carrera de Ingeniería..."
→ confidence: 0.9

EJEMPLO 15 - Carga horaria:
Usuario: "cuántas clases tiene el profesor Juan" o "cuál es la carga del docente García"
→ SÍ requiere BD
→ intent: "carga_docente"
→ entities: {{"nombre_docente": "Juan"}}
→ personalized_message: "Calculando {user_name}, estoy revisando la carga horaria del profesor Juan..."
→ confidence: 0.9

═══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES FINALES
═══════════════════════════════════════════════════════════════════════════════
1. SIEMPRE incluye el nombre del usuario ({user_name}) en el personalized_message
2. Extrae TODAS las entidades mencionadas, no dejes ninguna fuera
3. Si hay ambigüedad, usa tu mejor criterio pero explica en reasoning
4. La confianza debe ser realista según qué tan clara es la pregunta
5. Si la pregunta es muy vaga, pregunta aclaraciones en el mensaje

FORMATO JSON DE RESPUESTA - COMANDOS EXACTOS PARA EL ALGORITMO:
{{
    "intent": "tipo_de_intencion",
    "entities": {{
        "dia": null o número 1-7 (1=Lunes, 2=Martes, etc.) O número de día siguiente si dice "mañana",
        "hora": null o "HH:MM" en formato 24h EXACTO (ej: "09:00", "14:30", "08:00"),
        "turno": null o EXACTAMENTE "M"/"T"/"N" (M=Mañana, T=Tarde, N=Noche) - NO uses otras formas,
        "nombre_docente": null o string normalizado (ej: "Juan Pérez" o "Pérez"),
        "nombre_aula": null o string exacto del nombre en BD (ej: "A101", "L202"),
        "tipo_espacio": null o EXACTAMENTE uno de estos valores: "Laboratorio", "Teoria", "Auditorio" - 
                        SI menciona "laboratorio"/"lab"/"computos"/"computación"/"COMPUTOS" → "Laboratorio"
                        SI menciona "aula"/"salón"/"teórica" → "Teoria"
                        NO uses variaciones, SOLO estos valores exactos,
        "codigo_grupo": null o string exacto (ej: "GR001"),
        "nombre_materia": null o string (ej: "Matemáticas"),
        "nombre_carrera": null o string (ej: "Ingeniería"),
        "periodo_id": null o número (solo si mencionan período específico),
        "nombre_periodo": null o string (ej: "2024-I")
    }},
    "personalized_message": "Mensaje natural, amigable y personalizado. SIEMPRE incluye el nombre del usuario ({user_name}). Si requiere BD, explica QUÉ vas a buscar y CON QUÉ filtros.",
    "confidence": 0.0-1.0 (0.9+ alta confianza, 0.7-0.9 media, <0.7 baja),
    "reasoning": "Explicación breve: ¿Requiere BD? ¿Qué entidades detectaste? ¿Por qué elegiste esta intención?"
}}

⚠️ CRÍTICO - NORMALIZACIÓN DE COMANDOS:
El algoritmo (query_service) SOLO entiende valores exactos. NO puede interpretar.
TÚ (la IA) debes traducir TODO el lenguaje natural a comandos exactos:

1. tipo_espacio: 
   - "laboratorio"/"lab"/"computos"/"computación"/"COMPUTOS"/"cómputo" → "Laboratorio" EXACTO
   - "aula"/"salón"/"teórica"/"aula de teoría" → "Teoria" EXACTO
   - NO uses: "Aula de Teoría", "Laboratorio de Computos", etc. - Solo "Laboratorio" o "Teoria"

2. dia:
   - "mañana" = calcular número del día siguiente (1-7)
   - "hoy" = número del día actual
   - Nombres de días → números (1-7)

3. hora:
   - "9am"/"9 am"/"9:00 am" → "09:00"
   - "2pm"/"14:00" → "14:00"
   - SIEMPRE formato "HH:MM" en 24h

4. turno:
   - "mañana"/"AM"/"en la mañana" → "M"
   - "tarde"/"PM"/"en la tarde" → "T"
   - "noche"/"nocturno" → "N"

═══════════════════════════════════════════════════════════════════════════════
EJEMPLOS DETALLADOS POR CATEGORÍA
═══════════════════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES FINALES
═══════════════════════════════════════════════════════════════════════════════

1. SIEMPRE incluye el nombre del usuario ({user_name}) en el personalized_message
2. Extrae TODAS las entidades mencionadas en la pregunta, no dejes ninguna fuera
3. Si hay ambigüedad (ej: "mañana" puede ser día o turno), usa el contexto completo para decidir
4. La confianza debe ser realista: alta (0.9+) si la pregunta es clara, media (0.7-0.9) si hay algo de ambigüedad, baja (<0.7) si es muy vaga
5. Si la pregunta es muy vaga o ambigua, en el personalized_message pregunta aclaraciones de forma amigable
6. RAZONA ANTES DE RESPONDER: analiza el mensaje completo, identifica TODAS las entidades, y elige la intención más apropiada
7. Recuerda que puedes combinar filtros: día + hora + tipo de espacio, docente + día, etc.
"""
        
        user_prompt = f"""
Mensaje del usuario: "{user_message}"
{'(Contexto previo: ' + conversation_context + ')' if conversation_context else ''}

RAZONA PRIMERO:
1. ¿Qué está preguntando el usuario EXACTAMENTE?
2. ¿Qué tipo de entidad busca? (aula, laboratorio, docente, horario, etc.)
3. ¿Cuáles son las condiciones específicas? (día, hora, tipo, nombre, etc.)
4. ¿Cuál es la intención correcta de la lista?

Luego responde en formato JSON con tu análisis.
"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": 0.2,  # Baja temperatura para respuestas más consistentes
                "max_tokens": 1024,
                "return_citations": False  # No necesitamos citas web
            }
            
            # Intentar con retry automático para manejar rate limiting
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        response_text = data['choices'][0]['message']['content'].strip()
                        break
                    elif response.status_code == 429:
                        # Rate limit
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (attempt + 1)
                            print(f"⚠️  Rate limit alcanzado, esperando {wait_time} segundos...")
                            time.sleep(wait_time)
                            continue
                        else:
                            raise Exception(f"Rate limit: {response.status_code}")
                    else:
                        raise Exception(f"Error de API: {response.status_code} - {response.text}")
                        
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        print(f"⚠️  Error de conexión, reintentando en {wait_time} segundos...")
                        time.sleep(wait_time)
                        continue
                    raise
            
            # Extraer JSON de la respuesta
            # Limpiar markdown si viene con ```
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # Agregar mensaje personalizado si no viene
            if 'personalized_message' not in result:
                result['personalized_message'] = result.get('message', '')
            
            # Log del razonamiento si está disponible
            if 'reasoning' in result:
                print(f"🧠 Razonamiento: {result['reasoning']}")
            
            return result
            
        except json.JSONDecodeError as e:
            # Si no puede parsear JSON, usar valores por defecto
            print(f"⚠️ Error parseando JSON de Perplexity: {e}")
            print(f"   Respuesta recibida: {response_text[:200] if 'response_text' in locals() else 'N/A'}")
            return {
                'intent': 'desconocido',
                'entities': {},
                'personalized_message': f'Hola {user_name}, no pude entender completamente tu pregunta. ¿Podrías reformularla?',
                'confidence': 0.5
            }
        except Exception as e:
            import traceback
            print(f"⚠️ Error en Perplexity AI Service: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            traceback.print_exc()
            return {
                'intent': 'desconocido',
                'entities': {},
                'personalized_message': f'Lo siento {user_name}, hubo un error procesando tu mensaje. Por favor intenta de nuevo.',
                'confidence': 0.0
            }
    
    def format_schedule_to_natural_language(
        self,
        query_type: str,
        raw_data: List[Dict],
        user_name: str,
        initial_message: str = None
    ) -> str:
        """
        Toma datos de horarios y los traduce a lenguaje natural
        
        Args:
            query_type: Tipo de consulta
            raw_data: Datos con horarios (debe tener hora_inicio y hora_fin)
            user_name: Nombre del usuario
            initial_message: Mensaje inicial (opcional)
            
        Returns:
            Mensaje completo en lenguaje natural con horarios traducidos
        """
        if not raw_data:
            return initial_message or "No se encontraron resultados."
        
        # Detectar si los datos tienen estructura de horarios
        has_schedule_data = any(
            'hora_inicio' in item or 'hora_fin' in item 
            for item in raw_data[:3] if isinstance(item, dict)
        )
        
        if not has_schedule_data:
            # Si no son horarios, usar formato normal
            return initial_message or self._format_horarios_simple(raw_data, initial_message)
        
        # Preparar prompt para traducir horarios
        system_prompt = f"""Eres TIMO, un asistente que traduce datos de horarios a lenguaje natural.

INSTRUCCIONES:
Recibirás datos de horarios/disponibilidad con hora_inicio y hora_fin en formato "HH:MM".
Debes traducirlos a lenguaje natural entendible para el usuario.

FORMATO DE SALIDA:
- Para cada ítem, menciona el nombre y los horarios en lenguaje natural
- Usa formato: "desde las [hora] hasta las [hora]" o "[nombre]: libre desde [hora] hasta [hora]"
- Si hay múltiples horarios, lista cada uno claramente
- Sé conciso pero claro
- Convierte horas de "07:00" a "7:00" o "7:00 AM" según el contexto
- Si es después del mediodía, usa "2:00 PM" o formato 24h según sea más claro

EJEMPLOS:
Datos: {{"nombre": "A101", "hora_inicio": "07:00", "hora_fin": "10:00"}}
Salida: "A101: está libre desde las 7:00 hasta las 10:00"

Datos: {{"nombre": "LAB202", "hora_inicio": "09:00", "hora_fin": "12:00", "dia": "Lunes"}}
Salida: "El lunes, LAB202 está disponible desde las 9:00 hasta las 12:00"

Datos: {{"nombre": "A103", "hora_inicio": "14:00", "hora_fin": "16:00"}}
Salida: "A103: libre desde las 2:00 PM hasta las 4:00 PM" o "A103: libre desde las 14:00 hasta las 16:00"

Si hay un mensaje inicial, inclúyelo al principio.
Si son muchos resultados (>20), muestra un resumen y los primeros 20 detallados.
Organiza la información de forma clara y legible."""

        data_json = json.dumps(raw_data[:50], ensure_ascii=False, indent=2)  # Limitar a 50
        
        user_prompt = f"""Traduce estos datos de horarios a lenguaje natural para {user_name}:
{f'Mensaje inicial: {initial_message}' if initial_message else ''}

Datos:
{data_json}

Genera una respuesta clara en lenguaje natural, mencionando los horarios en formato legible.
Si hay múltiples horarios para el mismo espacio, agrupa la información claramente."""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                formatted = data['choices'][0]['message']['content'].strip()
                return formatted
            else:
                # Fallback simple
                return self._format_horarios_simple(raw_data, initial_message)
                
        except Exception as e:
            print(f"⚠️  Error traduciendo horarios: {e}")
            return self._format_horarios_simple(raw_data, initial_message)
    
    def _format_horarios_simple(self, data: List[Dict], initial_msg: str = None) -> str:
        """Formato simple de fallback para horarios"""
        result = initial_msg + "\n\n" if initial_msg else ""
        result += f"📋 **Resultados encontrados: {len(data)}**\n\n"
        
        for item in data[:20]:
            if isinstance(item, dict):
                nombre = item.get('nombre') or item.get('nombre_aula') or item.get('nombre_espacio', 'N/A')
                hora_inicio = item.get('hora_inicio', 'N/A')
                hora_fin = item.get('hora_fin', 'N/A')
                dia = item.get('dia', '')
                
                # Convertir hora_inicio de "07:00" a "7:00"
                if hora_inicio != 'N/A':
                    try:
                        h, m = hora_inicio.split(':')
                        hora_inicio = f"{int(h)}:{m}"
                    except:
                        pass
                
                if hora_fin != 'N/A':
                    try:
                        h, m = hora_fin.split(':')
                        hora_fin = f"{int(h)}:{m}"
                    except:
                        pass
                
                if hora_inicio != 'N/A' and hora_fin != 'N/A':
                    dia_str = f"{dia} - " if dia else ""
                    result += f"• {dia_str}{nombre}: disponible desde las {hora_inicio} hasta las {hora_fin}\n"
                else:
                    result += f"• {nombre}\n"
        
        if len(data) > 20:
            result += f"\n... y {len(data) - 20} más."
        
        return result
    
    def format_data_presentation(
        self,
        query_type: str,
        raw_data: List[Dict],
        user_name: str,
        user_role: str,
        intent_context: str = None
    ) -> str:
        """
        Formatea datos de BD en presentaciones bonitas (tablas, reportes, etc.)
        
        Args:
            query_type: Tipo de consulta (ej: 'aulas_disponibles', 'horarios_docente')
            raw_data: Lista de diccionarios con los datos crudos de la BD
            user_name: Nombre del usuario
            user_role: Rol del usuario
            intent_context: Contexto adicional sobre qué se consultó
            
        Returns:
            String formateado bonito para mostrar al usuario (tablas, listas, reportes)
        """
        if not raw_data or len(raw_data) == 0:
            return "No se encontraron resultados."
        
        # Preparar prompt para formatear los datos
        system_prompt = f"""Eres TIMO, un asistente inteligente que formatea datos de BD en presentaciones bonitas y legibles usando TABLAS MARKDOWN cuando sea apropiado.

CONTEXTO:
- Usuario: {user_name} ({user_role})
- Tipo de consulta: {query_type}
- Total de resultados: {len(raw_data)}
{f'- Contexto: {intent_context}' if intent_context else ''}

═══════════════════════════════════════════════════════════════════════════════
REGLAS DE FORMATEO - PREFERENCIA POR TABLAS
═══════════════════════════════════════════════════════════════════════════════

🎯 FORMATO PREFERIDO - TABLAS MARKDOWN:
- ⚠️ SIEMPRE que tengas 3 o más resultados estructurados, USA TABLAS MARKDOWN
- Las tablas son MÁS LEGIBLES y PROFESIONALES para datos estructurados
- Los usuarios prefieren tablas bien organizadas sobre listas largas

REGLA DE DECISIÓN:
1. ✅ 3-50 resultados estructurados → SIEMPRE usar TABLA MARKDOWN
2. ✅ Más de 50 resultados → Resumen + TABLA con primeros 20 + "y X más"
3. ⚠️ Menos de 3 resultados → Lista con viñetas está bien (pero tabla también funciona)

═══════════════════════════════════════════════════════════════════════════════
FORMATO DE TABLAS MARKDOWN (SINTAXIS EXACTA)
═══════════════════════════════════════════════════════════════════════════════

Formato básico (usa EXACTAMENTE esta sintaxis):

| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Dato 1    | Dato 2    | Dato 3    |
| Dato 4    | Dato 5    | Dato 6    |

REGLAS DE TABLAS:
- Encabezados descriptivos y claros (ej: "Nombre", "Tipo", "Capacidad", "Ubicación")
- Alineación consistente (generalmente izquierda)
- Separador de encabezado obligatorio: |-----------|-----------|-----------|
- Máximo 6-7 columnas para legibilidad
- Si hay muchas columnas, elige las más importantes

═══════════════════════════════════════════════════════════════════════════════
EJEMPLOS DE TABLAS POR TIPO DE CONSULTA
═══════════════════════════════════════════════════════════════════════════════

EJEMPLO 1 - Aulas/Laboratorios disponibles:
| Nombre | Tipo | Capacidad | Ubicación |
|--------|------|-----------|-----------|
| D_301  | Laboratorio | 50 | 3er piso |
| D_302  | Laboratorio | 50 | 3er piso |
| C_301  | Laboratorio | 50 | 3er piso |

EJEMPLO 2 - Horarios de docente:
| Día | Hora Inicio | Hora Fin | Aula | Materia |
|-----|-------------|----------|------|---------|
| Lunes | 08:00 | 10:00 | A101 | Matemáticas I |
| Miércoles | 14:00 | 16:00 | LAB202 | Programación |

EJEMPLO 3 - Docentes disponibles:
| Nombre Completo | Código | Especialidad |
|-----------------|--------|--------------|
| Juan Pérez | DOC001 | Matemáticas |
| María García | DOC002 | Física |

EJEMPLO 4 - Con muchos resultados (> 20):
📊 **Encontré 63 resultados. Mostrando los primeros 20:**

| Nombre | Tipo | Capacidad | Ubicación |
|--------|------|-----------|-----------|
| D_301  | Laboratorio | 50 | 3er piso |
| D_302  | Laboratorio | 50 | 3er piso |
... (y 43 más)

═══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES FINALES
═══════════════════════════════════════════════════════════════════════════════

✅ DEBES:
- Usar TABLAS MARKDOWN para 3+ resultados estructurados
- Elegir columnas relevantes según el tipo de consulta
- Incluir emojis cuando sea apropiado (📊, 📋, ✅, 🔍)
- Ser conciso pero completo
- Organizar información de forma lógica

❌ NO DEBES:
- Mostrar JSON crudo NUNCA
- Usar tablas para menos de 3 resultados (opcional)
- Incluir explicaciones adicionales, SOLO el formato
- Crear tablas con demasiadas columnas (>7)

Responde SOLO con el texto formateado (tabla/listas en Markdown), sin explicaciones adicionales."""

        # Convertir datos a JSON string
        data_json = json.dumps(raw_data[:50], ensure_ascii=False, indent=2)
        
        user_prompt = f"""Formatea estos datos en una presentación bonita y legible:

{data_json}

Genera una presentación clara y organizada para el usuario. NO muestres JSON crudo."""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                formatted = data['choices'][0]['message']['content'].strip()
                return formatted
            else:
                # Fallback: retornar datos en formato simple
                return self._format_simple_fallback_general(raw_data, query_type)
                
        except Exception as e:
            print(f"⚠️  Error formateando datos con IA: {e}")
            return self._format_simple_fallback_general(raw_data, query_type)
    
    def _format_simple_fallback_general(self, data: List[Dict], query_type: str) -> str:
        """Formato simple de fallback si la IA falla (versión general)"""
        if not data:
            return "No se encontraron resultados."
        
        result = f"📊 **Resultados encontrados: {len(data)}**\n\n"
        
        # Limitar a primeros 20 si son muchos
        display_data = data[:20]
        
        if len(data) > 20:
            result += f"*Mostrando los primeros 20 de {len(data)} resultados*\n\n"
        
        # Formato simple de lista
        for i, item in enumerate(display_data, 1):
            if isinstance(item, dict):
                # Formatear según el tipo de datos
                if 'nombre' in item:
                    nombre = item.get('nombre', 'N/A')
                    tipo = item.get('tipo', '')
                    capacidad = item.get('capacidad', '')
                    
                    info_parts = []
                    if tipo:
                        info_parts.append(f"Tipo: {tipo}")
                    if capacidad:
                        info_parts.append(f"Capacidad: {capacidad}")
                    
                    info_str = f" - {', '.join(info_parts)}" if info_parts else ""
                    result += f"• **{nombre}**{info_str}\n"
                else:
                    result += f"{i}. {item}\n"
            else:
                result += f"{i}. {item}\n"
        
        if len(data) > 20:
            result += f"\n... y {len(data) - 20} más."
        
        return result


