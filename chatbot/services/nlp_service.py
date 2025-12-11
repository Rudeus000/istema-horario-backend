"""
Servicio de Procesamiento de Lenguaje Natural (NLP)
Interpreta preguntas naturales del usuario y las convierte en intenciones estructuradas
"""
import re
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from .google_ai_service import GoogleAIService
from .perplexity_service import PerplexityAIService


class IntentType(Enum):
    """Tipos de intenciones que el chatbot puede reconocer"""
    AULAS_DISPONIBLES = "aulas_disponibles"
    DOCENTES_DISPONIBLES = "docentes_disponibles"
    HORARIOS_DOCENTE = "horarios_docente"
    HORARIOS_AULA = "horarios_aula"
    TIPOS_AULAS = "tipos_aulas"
    BUSCAR_DOCENTE = "buscar_docente"
    BUSCAR_AULA = "buscar_aula"
    CONFLICTOS = "conflictos"
    SALUDO = "saludo"
    DESPEDIDA = "despedida"
    AYUDA = "ayuda"
    DESCONOCIDO = "desconocido"
    # Nuevas intenciones avanzadas
    COMPARAR_DOCENTES = "comparar_docentes"
    COMPARAR_AULAS = "comparar_aulas"
    COMPARAR_PERIODOS = "comparar_periodos"
    HUECOS_HORARIOS = "huecos_horarios"
    HUECOS_DOCENTE = "huecos_docente"
    HUECOS_AULA = "huecos_aula"
    HUECOS_GRUPO = "huecos_grupo"
    CARGA_DOCENTE = "carga_docente"
    CARGA_AULA = "carga_aula"
    ESTADISTICAS_PERIODO = "estadisticas_periodo"
    BUSCAR_MATERIA = "buscar_materia"
    BUSCAR_CARRERA = "buscar_carrera"
    MATERIAS_CARRERA = "materias_carrera"
    GRUPOS_CARRERA = "grupos_carrera"
    HORARIOS_GRUPO = "horarios_grupo"
    ANALISIS_COMPLETO = "analisis_completo"


class NLPService:
    """Servicio para procesar lenguaje natural y extraer intenciones"""
    
    # Patrones para reconocer días de la semana
    DIAS_PATTERN = {
        r'\blunes\b': 1,
        r'\bmartes\b': 2,
        r'\bmi[eé]rcoles\b': 3,
        r'\bjueves\b': 4,
        r'\bviernes\b': 5,
        r'\bs[aá]bado\b': 6,
        r'\bdomingo\b': 7,
        r'\bma[ñn]ana\b': 'M',
        r'\btarde\b': 'T',
        r'\bnoche\b': 'N',
    }
    
    # Patrones para reconocer horas
    HORA_PATTERN = re.compile(r'(\d{1,2}):?(\d{2})?\s*(am|pm|AM|PM|horas)?')
    
    # Patrones de intención
    INTENT_PATTERNS = {
        IntentType.AULAS_DISPONIBLES: [
            r'aulas?\s+(disponibles|libres|vac[ií]as|sin\s+usar)',
            r'qu[eé]\s+aulas?\s+(hay|est[aá]n|tenemos)\s+(disponibles|libres)',
            r'aulas?\s+para\s+(el|la)\s*(d[ií]a|hora)',
            r'espacios?\s+(disponibles|libres)',
            r'sal[oó]n\s+(libre|disponible|vac[ií]o)',
            r'laboratorio\s+(libre|disponible|vac[ií]o)',
            r'(ma[ñn]ana|hoy|pasado)\s+(a\s+las?\s+)?\d+.*(sal[oó]n|aula|laboratorio)',
            r'(sal[oó]n|aula|laboratorio).*(libre|disponible).*(ma[ñn]ana|hoy|\d+)',
        ],
        IntentType.DOCENTES_DISPONIBLES: [
            r'docentes?\s+(disponibles|libres|sin\s+clases?)',
            r'profesores?\s+(disponibles|libres)',
            r'qu[eé]\s+docentes?\s+(est[aá]n|hay)\s+(libres|disponibles)',
        ],
        IntentType.HORARIOS_DOCENTE: [
            r'horario(s)?\s+(del|de|para)\s+docente',
            r'clases?\s+(del|de)\s+docente',
            r'qu[eé]\s+horario(s)?\s+tiene\s+(el|la)\s+docente',
        ],
        IntentType.HORARIOS_AULA: [
            r'horario(s)?\s+(del|de|para)\s+aula',
            r'qu[eé]\s+pasa\s+en\s+(el|la)\s+aula',
            r'clases?\s+en\s+(el|la)\s+aula',
        ],
        IntentType.TIPOS_AULAS: [
            r'tipos?\s+de\s+aulas?',
            r'qu[eé]\s+tipos?\s+de\s+espacios?\s+hay',
            r'clases?\s+de\s+aulas?',
        ],
        IntentType.BUSCAR_DOCENTE: [
            r'docente\s+(llamado|nombre|apellido)',
            r'profesor\s+(llamado|nombre)',
            r'buscar\s+docente',
        ],
        IntentType.BUSCAR_AULA: [
            r'aula\s+(llamada|nombre)',
            r'buscar\s+aula',
            r'espacio\s+(llamado|nombre)',
        ],
        IntentType.CONFLICTOS: [
            r'conflictos?',
            r'choques?\s+de\s+horarios?',
            r'problemas?\s+de\s+horarios?',
        ],
        IntentType.SALUDO: [
            r'\b(hola|buenos\s+d[ií]as|buenas\s+tardes|buenas\s+noches|hi|hello)\b',
        ],
        IntentType.DESPEDIDA: [
            r'\b(adios|chao|hasta\s+luego|nos\s+vemos|gracias)\b',
        ],
        IntentType.AYUDA: [
            r'\b(ayuda|help|qu[eé]\s+puedo\s+preguntar|qu[eé]\s+sabes)\b',
        ],
        # Nuevos patrones para intenciones avanzadas
        IntentType.HUECOS_HORARIOS: [
            r'huecos?\s+(libres?|disponibles?|vac[ií]os?)',
            r'd[óo]nde\s+hay\s+espacios?\s+libres?',
            r'qu[eé]\s+huecos?\s+hay',
            r'espacios?\s+vac[ií]os?\s+en\s+horarios?',
            r'horarios?\s+libres?',
        ],
        IntentType.HUECOS_DOCENTE: [
            r'huecos?\s+(del|de)\s+docente',
            r'qu[eé]\s+huecos?\s+tiene\s+(el|la)\s+docente',
            r'horarios?\s+libres?\s+(del|de)\s+docente',
            r'docente\s+(.*?)\s+(libre|disponible|huecos?)',
        ],
        IntentType.HUECOS_AULA: [
            r'huecos?\s+(del|de)\s+aula',
            r'qu[eé]\s+huecos?\s+tiene\s+(el|la)\s+aula',
            r'aula\s+(.*?)\s+(libre|disponible)',
        ],
        IntentType.HUECOS_GRUPO: [
            r'huecos?\s+(del|de)\s+grupo',
            r'qu[eé]\s+huecos?\s+tiene\s+(el|la)\s+grupo',
            r'horarios?\s+libres?\s+(del|de)\s+grupo',
        ],
        IntentType.COMPARAR_DOCENTES: [
            r'comparar?\s+docentes?',
            r'compara?\s+la\s+carga\s+(del|de)',
            r'qu[ié]n\s+tiene\s+m[aá]s\s+clases?',
            r'diferencias?\s+entre\s+docentes?',
        ],
        IntentType.COMPARAR_AULAS: [
            r'comparar?\s+aulas?',
            r'compara?\s+(el|la)\s+uso\s+(del|de)\s+aulas?',
            r'qu[eé]\s+aula\s+se\s+usa\s+m[aá]s',
        ],
        IntentType.CARGA_DOCENTE: [
            r'carga\s+(del|de)\s+docente',
            r'cu[aá]ntas?\s+clases?\s+tiene\s+(el|la)\s+docente',
            r'horas?\s+(del|de)\s+docente',
        ],
        IntentType.CARGA_AULA: [
            r'carga\s+(del|de)\s+aula',
            r'cu[aá]ntas?\s+clases?\s+se\s+dan\s+en',
            r'uso\s+(del|de)\s+aula',
        ],
        IntentType.ESTADISTICAS_PERIODO: [
            r'estad[ií]sticas?\s+(del|de)\s+per[ií]odo',
            r'resumen\s+(del|de)\s+per[ií]odo',
            r'dame\s+un\s+an[aá]lisis',
            r'estad[ií]sticas?\s+generales?',
            r'resumen\s+general',
        ],
        IntentType.BUSCAR_MATERIA: [
            r'buscar?\s+materia',
            r'qu[eé]\s+materias?\s+hay',
            r'materia\s+(llamada|nombre|codigo)',
            r'asignatura\s+(llamada|nombre)',
        ],
        IntentType.BUSCAR_CARRERA: [
            r'buscar?\s+carrera',
            r'qu[eé]\s+carreras?\s+hay',
            r'carrera\s+(llamada|nombre)',
        ],
        IntentType.MATERIAS_CARRERA: [
            r'materias?\s+(del|de)\s+carrera',
            r'qu[eé]\s+materias?\s+tiene\s+la\s+carrera',
            r'asignaturas?\s+(del|de)\s+carrera',
        ],
        IntentType.GRUPOS_CARRERA: [
            r'grupos?\s+(del|de)\s+carrera',
            r'qu[eé]\s+grupos?\s+tiene\s+la\s+carrera',
            r'secciones?\s+(del|de)\s+carrera',
        ],
        IntentType.HORARIOS_GRUPO: [
            r'horario(s)?\s+(del|de)\s+grupo',
            r'qu[eé]\s+horario(s)?\s+tiene\s+(el|la)\s+grupo',
            r'clases?\s+(del|de)\s+grupo',
        ],
        IntentType.ANALISIS_COMPLETO: [
            r'an[aá]lisis?\s+completo',
            r'reporte\s+completo',
            r'dame\s+todo',
            r'informe\s+general',
        ],
    }
    
    def __init__(self, use_ai: bool = True, google_ai_api_key: Optional[str] = None, perplexity_api_key: Optional[str] = None):
        """
        Inicializa el servicio NLP
        
        Args:
            use_ai: Si es True, usa IA (Perplexity si está disponible, sino Google AI). Si False, usa patrones regex.
            google_ai_api_key: Clave de API de Google AI (opcional)
            perplexity_api_key: Clave de API de Perplexity AI (opcional, tiene prioridad)
        """
        self.use_ai = use_ai
        self.google_ai_api_key = google_ai_api_key or os.getenv('GOOGLE_AI_API_KEY')
        self.perplexity_api_key = perplexity_api_key or os.getenv('PERPLEXITY_API_KEY')
        
        self.google_ai_service = None
        self.perplexity_service = None
        
        # Prioridad: Perplexity > Google AI > Regex
        if use_ai and self.perplexity_api_key:
            try:
                self.perplexity_service = PerplexityAIService(self.perplexity_api_key)
                print("✅ Perplexity AI inicializado correctamente")
            except Exception as e:
                print(f"⚠️  Error inicializando Perplexity AI: {e}. Intentando con Google AI...")
                self.perplexity_service = None
                
        if use_ai and not self.perplexity_service and self.google_ai_api_key:
            try:
                self.google_ai_service = GoogleAIService(self.google_ai_api_key)
                print("✅ Google AI inicializado correctamente")
            except Exception as e:
                print(f"⚠️  Error inicializando Google AI: {e}. Usando modo regex.")
                self.use_ai = False
                self.google_ai_service = None
        elif use_ai and not self.perplexity_service and not self.google_ai_api_key:
            print("⚠️  No hay API keys configuradas. Usando modo regex.")
            self.use_ai = False
    
    def process(
        self, 
        user_message: str,
        user_name: str = "Usuario",
        user_role: str = "Usuario",
        conversation_context: Optional[str] = None
    ) -> Dict:
        """
        Procesa un mensaje del usuario y retorna la intención estructurada
        
        Args:
            user_message: Mensaje del usuario en lenguaje natural
            user_name: Nombre del usuario (para personalización)
            user_role: Rol del usuario (para personalización)
            conversation_context: Contexto de conversación previa (opcional)
            
        Returns:
            Dict con:
                - intent: IntentType
                - entities: Dict con entidades extraídas (dia, hora, turno, nombre, etc.)
                - confidence: float (0-1)
                - original_message: str
                - personalized_message: str (mensaje personalizado de Google AI)
        """
        user_message_lower = user_message.lower().strip()
        
        # Prioridad: Perplexity > Google AI > Regex
        if self.use_ai and self.perplexity_service:
            return self._process_with_perplexity(
                user_message, user_name, user_role, conversation_context
            )
        elif self.use_ai and self.google_ai_service:
            return self._process_with_google_ai(
                user_message, user_name, user_role, conversation_context
            )
        else:
            return self._process_with_regex(user_message_lower, user_message, user_name)
    
    def _process_with_regex(self, message_lower: str, original_message: str, user_name: str = "Usuario") -> Dict:
        """Procesa el mensaje usando patrones regex"""
        best_intent = IntentType.DESCONOCIDO
        best_confidence = 0.0
        entities = {}
        
        # Detectar intención
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, message_lower, re.IGNORECASE)
                if matches:
                    confidence = min(1.0, len(list(matches)) * 0.3 + 0.5)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent_type
        
        # Extraer entidades
        entities.update(self._extract_days(message_lower))
        entities.update(self._extract_times(message_lower))
        entities.update(self._extract_names(message_lower))
        entities.update(self._extract_periodo(message_lower))
        entities.update(self._extract_tipo_espacio(message_lower))
        
        # Generar mensaje personalizado básico según el intent detectado
        personalized_message = self._generate_basic_message(best_intent, entities, user_name, original_message)
        
        return {
            'intent': best_intent,
            'entities': entities,
            'confidence': best_confidence,
            'original_message': original_message,
            'personalized_message': personalized_message,
        }
    
    def _generate_basic_message(self, intent: IntentType, entities: Dict, user_name: str, original_message: str) -> str:
        """Genera un mensaje básico personalizado cuando se usa regex fallback"""
        if intent == IntentType.AULAS_DISPONIBLES:
            tipo = entities.get('tipo_espacio') or entities.get('tipo_aula', 'espacios')
            hora = entities.get('hora', '')
            dia = entities.get('dia', '')
            
            parts = [f"Hola {user_name}"]
            parts.append(f"Voy a buscar {tipo.lower() if tipo else 'espacios'} disponibles")
            
            if hora:
                parts.append(f"a las {hora}")
            if dia:
                dias_map = {1: 'lunes', 2: 'martes', 3: 'miércoles', 4: 'jueves', 
                           5: 'viernes', 6: 'sábado', 7: 'domingo'}
                dia_nombre = dias_map.get(dia, f'día {dia}')
                parts.append(f"el {dia_nombre}")
            
            parts.append("para ti...")
            return " ".join(parts) + " 🔍"
        
        elif intent == IntentType.DOCENTES_DISPONIBLES:
            return f"Hola {user_name}, estoy buscando docentes disponibles... 👨‍🏫"
        
        elif intent == IntentType.HORARIOS_DOCENTE:
            nombre = entities.get('nombre_docente', 'el docente')
            return f"Consultando {user_name}, estoy buscando los horarios de {nombre}... 📅"
        
        elif intent == IntentType.HORARIOS_AULA:
            nombre_aula = entities.get('nombre_aula', 'el aula')
            return f"Revisando {user_name}, estoy buscando los horarios del {nombre_aula}... 📋"
        
        elif intent == IntentType.SALUDO:
            return f"¡Hola {user_name}! 👋 Soy TIMO, tu asistente de horarios. ¿En qué te puedo ayudar hoy?"
        
        elif intent == IntentType.AYUDA:
            return f"Hola {user_name}, puedo ayudarte con:\n• Consultar aulas/laboratorios disponibles\n• Ver horarios de docentes\n• Buscar docentes disponibles\n• Y mucho más. ¿Qué necesitas?"
        
        elif intent == IntentType.DESPEDIDA:
            return f"¡Hasta luego {user_name}! Que tengas un buen día. 👋"
        
        else:
            return f"Hola {user_name}, estoy procesando tu consulta... 🔍"
    
    def _process_with_perplexity(
        self,
        user_message: str,
        user_name: str,
        user_role: str,
        conversation_context: Optional[str]
    ) -> Dict:
        """Procesa el mensaje usando Perplexity AI con fallback a regex"""
        try:
            result = self.perplexity_service.process_message(
                user_message, user_name, user_role, conversation_context
            )
            
            # Si Perplexity retorna 'desconocido' con baja confianza, usar fallback
            intent_str = result.get('intent', 'desconocido')
            confidence = result.get('confidence', 0.0)
            
            # Si es desconocido (con baja confianza), intentar con regex
            if intent_str == 'desconocido' or confidence < 0.3:
                print(f"⚠️  Perplexity retornó '{intent_str}' con confianza {confidence}. Intentando con regex como fallback...")
                regex_result = self._process_with_regex(user_message.lower(), user_message, user_name)
                # Si regex encuentra algo mejor que DESCONOCIDO, usarlo
                if regex_result.get('intent') != IntentType.DESCONOCIDO:
                    print(f"✅ Regex encontró intent: {regex_result.get('intent')}")
                    return regex_result
            
            # Convertir intent string a IntentType
            intent_str = result.get('intent', 'desconocido')
            # Normalizar el string a lowercase
            intent_str = str(intent_str).lower().strip()
            print(f"🔍 Intent recibido de Perplexity: '{intent_str}'")
            
            try:
                # Intentar convertir directamente usando el valor del enum
                intent = IntentType(intent_str)
                print(f"✅ Intent convertido exitosamente: {intent}")
            except (ValueError, AttributeError) as e:
                # Si falla, intentar encontrar el enum correspondiente por valor
                print(f"⚠️  No se pudo convertir '{intent_str}' directamente, buscando en enum...")
                intent = IntentType.DESCONOCIDO
                for intent_type in IntentType:
                    if intent_type.value == intent_str:
                        intent = intent_type
                        print(f"✅ Intent encontrado por búsqueda: {intent}")
                        break
                if intent == IntentType.DESCONOCIDO:
                    print(f"❌ Intent '{intent_str}' no reconocido, usando DESCONOCIDO")
                    # Si no se encuentra, usar regex como último recurso
                    print(f"🔄 Intentando con regex como último recurso...")
                    regex_result = self._process_with_regex(user_message.lower(), user_message, user_name)
                    return regex_result
            
            return {
                'intent': intent,
                'entities': result.get('entities', {}),
                'confidence': result.get('confidence', 0.7),
                'original_message': user_message,
                'personalized_message': result.get('personalized_message', ''),
            }
        except Exception as e:
            # Si Perplexity falla completamente, usar regex como fallback
            print(f"⚠️  Error usando Perplexity: {e}. Usando modo regex como fallback...")
            import traceback
            traceback.print_exc()
            return self._process_with_regex(user_message.lower(), user_message, user_name)
    
    def _process_with_google_ai(
        self,
        user_message: str,
        user_name: str,
        user_role: str,
        conversation_context: Optional[str]
    ) -> Dict:
        """Procesa el mensaje usando Google AI con fallback a regex"""
        try:
            result = self.google_ai_service.process_message(
                user_message, user_name, user_role, conversation_context
            )
            
            # Si Google AI retorna 'desconocido' con baja confianza, usar fallback
            intent_str = result.get('intent', 'desconocido')
            confidence = result.get('confidence', 0.0)
            
            # Si es desconocido (con baja confianza o si el intent no se pudo convertir), intentar con regex
            if intent_str == 'desconocido' or confidence < 0.3:
                print(f"⚠️  Google AI retornó '{intent_str}' con confianza {confidence}. Intentando con regex como fallback...")
                regex_result = self._process_with_regex(user_message.lower(), user_message, user_name)
                # Si regex encuentra algo mejor que DESCONOCIDO, usarlo
                if regex_result.get('intent') != IntentType.DESCONOCIDO:
                    print(f"✅ Regex encontró intent: {regex_result.get('intent')}")
                    return regex_result
            
            # Convertir intent string a IntentType
            intent_str = result.get('intent', 'desconocido')
            # Normalizar el string a lowercase
            intent_str = str(intent_str).lower().strip()
            print(f"🔍 Intent recibido de Google AI: '{intent_str}'")
            
            try:
                # Intentar convertir directamente usando el valor del enum
                # IntentType usa el valor como string (ej: 'aulas_disponibles')
                intent = IntentType(intent_str)
                print(f"✅ Intent convertido exitosamente: {intent}")
            except (ValueError, AttributeError) as e:
                # Si falla, intentar encontrar el enum correspondiente por valor
                print(f"⚠️  No se pudo convertir '{intent_str}' directamente, buscando en enum...")
                intent = IntentType.DESCONOCIDO
                for intent_type in IntentType:
                    if intent_type.value == intent_str:
                        intent = intent_type
                        print(f"✅ Intent encontrado por búsqueda: {intent}")
                        break
                if intent == IntentType.DESCONOCIDO:
                    print(f"❌ Intent '{intent_str}' no reconocido, usando DESCONOCIDO")
                    # Si no se encuentra, usar regex como último recurso
                    print(f"🔄 Intentando con regex como último recurso...")
                    regex_result = self._process_with_regex(user_message.lower(), user_message, user_name)
                    return regex_result
            
            return {
                'intent': intent,
                'entities': result.get('entities', {}),
                'confidence': result.get('confidence', 0.7),
                'original_message': user_message,
                'personalized_message': result.get('personalized_message', ''),
            }
        except Exception as e:
            # Si Google AI falla completamente, usar regex como fallback
            print(f"⚠️  Error usando Google AI: {e}. Usando modo regex como fallback...")
            import traceback
            traceback.print_exc()
            return self._process_with_regex(user_message.lower(), user_message, user_name)
    
    def _extract_days(self, message: str) -> Dict:
        """Extrae días de la semana y turnos"""
        entities = {}
        for pattern, value in self.DIAS_PATTERN.items():
            if re.search(pattern, message, re.IGNORECASE):
                if isinstance(value, int):
                    entities['dia'] = value
                else:
                    entities['turno'] = value
        return entities
    
    def _extract_times(self, message: str) -> Dict:
        """Extrae horas del mensaje"""
        entities = {}
        matches = self.HORA_PATTERN.findall(message)
        if matches:
            hora, minutos, periodo = matches[0]
            hora_int = int(hora)
            minutos_int = int(minutos) if minutos else 0
            
            # Convertir a formato 24h si es PM
            if periodo and periodo.lower() == 'pm' and hora_int < 12:
                hora_int += 12
            
            entities['hora'] = f"{hora_int:02d}:{minutos_int:02d}"
        return entities
    
    def _extract_names(self, message: str) -> Dict:
        """Extrae nombres de docentes o aulas (básico)"""
        entities = {}
        # Patrones simples para nombres propios
        # Se puede mejorar con NER si se usa IA
        nombre_pattern = r'\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)\b'
        matches = re.findall(nombre_pattern, message)
        if matches:
            # Asumir que el primer nombre completo es el docente o aula
            entities['nombre'] = matches[0]
        return entities
    
    def _extract_periodo(self, message: str) -> Dict:
        """Extrae información sobre período académico"""
        entities = {}
        periodo_patterns = {
            r'\b(\d{4})\s*(I|II|1|2)\b': 'periodo',
            r'\b(primer|segundo)\s+semestre\b': 'periodo',
        }
        for pattern, key in periodo_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                entities[key] = True
        return entities
    
    def _extract_tipo_espacio(self, message: str) -> Dict:
        """Extrae el tipo de espacio (laboratorio, aula, etc.) del mensaje"""
        entities = {}
        message_lower = message.lower()
        
        # Detectar laboratorios (prioridad alta) - buscar variaciones comunes
        if re.search(r'\b(laboratorio|lab|laboratorios|labs|computo|computos|computaci[oó]n)\b', message_lower):
            entities['tipo_espacio'] = 'Laboratorio'
            entities['tipo_aula'] = 'Laboratorio'  # También agregar tipo_aula para compatibilidad
        # Detectar aulas teóricas específicamente
        elif re.search(r'\b(aula|aulas|sal[oó]n|salones)\s+(te[oó]ric|normal|com[uú]n)\b', message_lower):
            entities['tipo_espacio'] = 'Teoria'
            entities['tipo_aula'] = 'Teoria'
        # Si menciona "aula" o "salón" sin especificar tipo, no agregar tipo (buscar todos)
        
        return entities


# Instancia global del servicio (se puede configurar para usar IA)
nlp_service = NLPService(use_ai=False)

