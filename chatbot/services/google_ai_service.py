"""
Servicio de Google AI (Gemini) como intermediario NLP
"""
import json
import os
import time
import google.generativeai as genai
from typing import Dict, Optional
from google.api_core import retry


class GoogleAIService:
    """Servicio para usar Google Gemini como intermediario NLP"""
    
    def __init__(self, api_key: str):
        """
        Inicializa el servicio de Google AI
        
        Args:
            api_key: API key de Google AI
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Usar gemini-2.5-flash (más rápido) o gemini-2.5-pro (mejor calidad)
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception:
            # Fallback a gemini-2.5-pro si flash no está disponible
            try:
                self.model = genai.GenerativeModel('gemini-2.5-pro')
            except Exception:
                # Último fallback a versión latest
                try:
                    self.model = genai.GenerativeModel('gemini-pro-latest')
                except Exception:
                    raise Exception("No se pudo inicializar ningún modelo de Google AI")
    
    def process_message(
        self, 
        user_message: str, 
        user_name: str,
        user_role: str,
        conversation_context: Optional[str] = None
    ) -> Dict:
        """
        Procesa un mensaje del usuario usando Google AI
        
        Args:
            user_message: Mensaje del usuario
            user_name: Nombre del usuario
            user_role: Rol del usuario (ej: 'Administrador', 'Docente', 'Coordinador')
            conversation_context: Contexto de conversación previa (opcional)
            
        Returns:
            Dict con intent, entities, y mensaje personalizado
        """
        # Construir prompt con contexto del usuario
        system_prompt = f"""Eres un asistente inteligente del sistema de gestión de horarios académicos de La Pontificia.

CONTEXTO DEL USUARIO:
- Nombre: {user_name}
- Rol: {user_role}

El sistema tiene las siguientes capacidades:
1. Consultar aulas/laboratorios/salones disponibles por día/hora/tipo
   - Ejemplo: "¿Qué laboratorios de computación están libres mañana a las 9am?"
   - Ejemplo: "¿Hay algún salón disponible el lunes a las 8?"
2. Consultar docentes disponibles/libres
3. Ver horarios de docentes, aulas, grupos
4. Detectar huecos libres en horarios
5. Comparar carga horaria entre docentes/aulas
6. Generar estadísticas del período
7. Buscar materias, carreras, grupos
8. Detectar conflictos de horarios

IMPORTANTE: "aulas", "salones", "laboratorios" son términos intercambiables. Si preguntan sobre un tipo específico de espacio (como "laboratorio de COMPUTOS"), usa la entidad "nombre_aula" o "tipo_aula".

CAPACIDADES POR ROL:
- Administrador: Acceso completo a todas las consultas
- Coordinador Académico: Puede consultar todo excepto información sensible de otros coordinadores
- Docente: Puede ver sus propios horarios, huecos, y consultas básicas de aulas/disponibilidad

INSTRUCCIONES:
1. Analiza el mensaje del usuario y determina qué quiere hacer
2. Extrae entidades relevantes (días, horas, nombres, etc.)
3. Responde de forma natural y amigable, usando el nombre del usuario
4. Personaliza la respuesta según el rol del usuario
5. Si el usuario no especifica bien su consulta, sé proactivo y sugiere opciones

RESPUESTA EN FORMATO JSON:
{{
    "intent": "tipo_de_intencion",
    "entities": {{
        "dia": null o número 1-7,
        "hora": null o "HH:MM",
        "turno": null o "M"/"T"/"N",
        "nombre_docente": null o string,
        "nombre_aula": null o string,
        "codigo_grupo": null o string,
        "nombre_materia": null o string,
        "nombre_carrera": null o string
    }},
    "personalized_message": "Mensaje natural y amigable para el usuario",
    "confidence": 0.0-1.0
}}

TIPOS DE INTENCIÓN POSIBLES:
- aulas_disponibles
- docentes_disponibles
- horarios_docente
- horarios_aula
- tipos_aulas
- buscar_docente
- buscar_aula
- huecos_horarios
- huecos_docente
- huecos_aula
- huecos_grupo
- comparar_docentes
- comparar_aulas
- carga_docente
- carga_aula
- estadisticas_periodo
- buscar_materia
- buscar_carrera
- materias_carrera
- grupos_carrera
- horarios_grupo
- analisis_completo
- conflictos
- saludo
- despedida
- ayuda
"""
        
        user_prompt = f"""
Mensaje del usuario: "{user_message}"
{'(Contexto previo: ' + conversation_context + ')' if conversation_context else ''}

Analiza la intención y responde en formato JSON.
"""
        
        try:
            # Configuración de generación
            generation_config = {
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            # Intentar con retry automático para manejar rate limiting
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(
                        system_prompt + "\n\n" + user_prompt,
                        generation_config=generation_config
                    )
                    break  # Éxito, salir del loop
                except Exception as e:
                    error_str = str(e)
                    # Si es rate limit, esperar y reintentar
                    if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                        if attempt < max_retries - 1:
                            # Extraer tiempo de espera del error si está disponible
                            wait_time = retry_delay * (attempt + 1)
                            print(f"⚠️  Rate limit alcanzado, esperando {wait_time} segundos...")
                            time.sleep(wait_time)
                            continue
                    raise  # Si no es rate limit o se agotaron los reintentos, lanzar error
            
            # Extraer JSON de la respuesta
            response_text = response.text.strip()
            
            # Limpiar markdown si viene con ```
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Intentar reparar JSON si está truncado
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as parse_error:
                # Intentar reparar JSON truncado
                print(f"⚠️  JSON truncado detectado, intentando reparar...")
                try:
                    # Si el JSON está truncado, intentar cerrar los objetos/arrays abiertos
                    repaired_text = response_text
                    
                    # Contar llaves y corchetes abiertos
                    open_braces = repaired_text.count('{') - repaired_text.count('}')
                    open_brackets = repaired_text.count('[') - repaired_text.count(']')
                    
                    # Cerrar objetos/arrays abiertos
                    repaired_text += '\n' + '}' * open_braces + ']' * open_brackets
                    
                    result = json.loads(repaired_text)
                    print(f"✅ JSON reparado exitosamente")
                except:
                    # Si no se puede reparar, lanzar el error original
                    raise parse_error
            
            result = json.loads(response_text) if 'result' not in locals() else result
            
            # Agregar mensaje personalizado si no viene
            if 'personalized_message' not in result:
                result['personalized_message'] = result.get('message', '')
            
            return result
            
        except json.JSONDecodeError as e:
            # Si no puede parsear JSON, usar valores por defecto
            print(f"⚠️ Error parseando JSON de Google AI: {e}")
            print(f"   Respuesta recibida: {response_text[:200] if 'response_text' in locals() else 'N/A'}")
            return {
                'intent': 'desconocido',
                'entities': {},
                'personalized_message': f'Hola {user_name}, no pude entender completamente tu pregunta. ¿Podrías reformularla?',
                'confidence': 0.5
            }
        except Exception as e:
            import traceback
            print(f"⚠️ Error en Google AI Service: {e}")
            print(f"   Tipo de error: {type(e).__name__}")
            traceback.print_exc()
            return {
                'intent': 'desconocido',
                'entities': {},
                'personalized_message': f'Lo siento {user_name}, hubo un error procesando tu mensaje. Por favor intenta de nuevo.',
                'confidence': 0.0
            }

