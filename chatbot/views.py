"""
Vistas API para el chatbot
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .serializers import ChatMessageSerializer, ChatResponseSerializer
from .services.nlp_service import NLPService, IntentType
from .services.query_service import QueryService
from decouple import config


# Inicializar servicios con Perplexity (prioridad) o Google AI como fallback
# Leer API keys directamente de config para evitar problemas de inicialización
_perplexity_key = config('PERPLEXITY_API_KEY', default='')
_google_ai_key = config('GOOGLE_AI_API_KEY', default='')
nlp_service = NLPService(
    use_ai=True if (_perplexity_key or _google_ai_key) else False, 
    perplexity_api_key=_perplexity_key,
    google_ai_api_key=_google_ai_key
)
query_service = QueryService()


def _format_data_fallback_simple(data: list, query_type: str, initial_message: str = '') -> str:
    """
    Formatea datos en lenguaje natural simple (fallback cuando no hay IA disponible)
    """
    if not data:
        return initial_message or "No se encontraron resultados."
    
    result_parts = []
    if initial_message:
        result_parts.append(initial_message)
    
    result_parts.append(f"\n📊 **Encontré {len(data)} resultado(s):**\n")
    
    # Limitar a primeros 20 si son muchos
    display_data = data[:20]
    
    if len(data) > 20:
        result_parts.append(f"*Mostrando los primeros 20 de {len(data)} resultados*\n")
    
    # Formatear cada resultado
    for i, item in enumerate(display_data, 1):
        if isinstance(item, dict):
            if 'nombre' in item:
                nombre = item.get('nombre', 'N/A')
                tipo = item.get('tipo', '')
                capacidad = item.get('capacidad', '')
                ubicacion = item.get('ubicacion', '')
                
                info_parts = []
                if tipo:
                    info_parts.append(f"**{tipo}**")
                if capacidad:
                    info_parts.append(f"Capacidad: {capacidad} personas")
                if ubicacion:
                    info_parts.append(f"Ubicación: {ubicacion}")
                
                info_str = f" - {', '.join(info_parts)}" if info_parts else ""
                result_parts.append(f"• **{nombre}**{info_str}")
            else:
                # Si no tiene 'nombre', mostrar todos los campos importantes
                important_fields = {k: v for k, v in item.items() if k not in ['id']}
                fields_str = ', '.join([f"{k}: {v}" for k, v in important_fields.items()])
                result_parts.append(f"• {fields_str}")
        else:
            result_parts.append(f"{i}. {item}")
    
    if len(data) > 20:
        result_parts.append(f"\n... y {len(data) - 20} resultado(s) más.")
    
    return "\n".join(result_parts)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    Endpoint principal del chatbot
    
    Recibe un mensaje del usuario, lo procesa con NLP,
    ejecuta la consulta correspondiente y retorna la respuesta.
    
    POST /api/chatbot/chat/
    {
        "message": "¿Qué aulas están disponibles el lunes a las 8:00?",
        "conversation_id": "optional-conversation-id"
    }
    """
    serializer = ChatMessageSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Mensaje inválido', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_message = serializer.validated_data.get('message')
    conversation_id = serializer.validated_data.get('conversation_id', '')
    
    # Obtener información del usuario
    user = request.user
    user_name = user.get_full_name() or user.username
    user_groups = user.groups.all()
    user_role = user_groups.first().name if user_groups.exists() else 'Usuario'
    
    # Si es docente, priorizar rol de docente
    if hasattr(user, 'perfil_docente') and user.perfil_docente:
        docente = user.perfil_docente
        user_name = f"{docente.nombres} {docente.apellidos}"
        user_role = 'Docente'
    
    try:
        # Procesar el mensaje con NLP (incluye contexto del usuario)
        intent_data = nlp_service.process(
            user_message=user_message,
            user_name=user_name,
            user_role=user_role,
            conversation_context=conversation_id
        )
        
        # Log para debug: ver qué entidades detectó la IA
        print(f"\n🔍 DEBUG - Entidades detectadas:")
        print(f"   Intent: {intent_data.get('intent')}")
        print(f"   Entities: {intent_data.get('entities', {})}")
        print(f"   Confidence: {intent_data.get('confidence', 0.0)}")
        print(f"   Personalized message: {intent_data.get('personalized_message', 'N/A')[:100]}...")
        print()
        
        # Determinar si la intención requiere datos de BD
        intent = intent_data.get('intent')
        confidence = intent_data.get('confidence', 0.0)
        personalized_message = intent_data.get('personalized_message')
        
        intent_requires_data = intent and intent not in [
            IntentType.SALUDO, 
            IntentType.DESPEDIDA, 
            IntentType.AYUDA,
            IntentType.DESCONOCIDO
        ]
        
        # IMPORTANTE: Si la IA falló (no hay mensaje Y baja confianza), NO ejecutar consultas
        # Solo ejecutar si hay mensaje de la IA o si la confianza es aceptable
        if not personalized_message and confidence < 0.5 and intent == IntentType.DESCONOCIDO:
            # La IA falló completamente, no ejecutar consultas
            return Response({
                'success': False,
                'message': 'No pude entender tu pregunta. Por favor reformula o intenta con preguntas como:\n• ¿Qué laboratorios están disponibles el lunes a las 8?\n• ¿Qué aulas hay libres mañana?\n• ¿Qué docentes están disponibles?',
                'data': None,
                'confidence': confidence,
                'intent': 'desconocido' if not intent else (intent.value if hasattr(intent, 'value') else str(intent)),
                'user_name': user_name,
                'user_role': user_role
            }, status=200)
        
        # Ejecutar la consulta solo si la intención requiere datos
        if intent_requires_data:
            result = query_service.execute_query(
                intent_data, 
                user=user, 
                user_role=user_role
            )
        else:
            # No requiere datos, crear respuesta vacía
            result = {
                'success': True,
                'data': None,
                'message': '',
                'query_type': str(intent.value) if hasattr(intent, 'value') else str(intent) if intent else 'unknown'
            }
        
        # SIEMPRE usar el mensaje de la IA si está disponible (tiene máxima prioridad)
        if personalized_message:
            result['message'] = personalized_message  # Mensaje de la IA
            # Si la intención NO requiere datos, eliminar los datos
            if not intent_requires_data:
                result['data'] = None
        # Si no hay mensaje de la IA pero la consulta se ejecutó, generar mensaje genérico
        elif not result.get('message') and intent_requires_data:
            result['message'] = 'Consulté la base de datos pero no pude generar un mensaje personalizado. Por favor intenta de nuevo.'
        elif not result.get('message'):
            result['message'] = 'No pude generar una respuesta. Por favor intenta de nuevo.'
        
        # Si hay datos, formatearlos a lenguaje natural (no solo horarios, TODOS los resultados)
        if intent_requires_data and result.get('data') and isinstance(result.get('data'), list):
            query_data = result['data']
            data_count = len(query_data)
            
            # Formatear TODOS los resultados a lenguaje natural
            # SIEMPRE formatear, incluso si no hay IA disponible (usará fallback)
            if data_count > 0:
                try:
                    print(f"🔄 Formateando {data_count} resultados a lenguaje natural...")
                    
                    # Detectar si los datos tienen estructura de horarios
                    has_schedule_info = (
                        isinstance(query_data[0], dict) and
                        any(key in query_data[0] for key in ['hora_inicio', 'hora_fin', 'bloque_horario'])
                    )
                    
                    formatted_data_text = None
                    
                    if has_schedule_info and nlp_service.perplexity_service:
                        # Si tiene horarios y hay IA disponible, usar el método especializado
                        formatted_data_text = nlp_service.perplexity_service.format_schedule_to_natural_language(
                            query_type=result.get('query_type', ''),
                            raw_data=query_data,
                            user_name=user_name,
                            initial_message=result.get('message')  # Mensaje inicial de la IA
                        )
                    elif nlp_service.perplexity_service:
                        # Si no tiene horarios pero hay IA disponible, formatear como lista normal
                        formatted_data_text = nlp_service.perplexity_service.format_data_presentation(
                            query_type=result.get('query_type', ''),
                            raw_data=query_data,
                            user_name=user_name,
                            user_role=user_role,
                            intent_context=result.get('message')
                        )
                    else:
                        # Si no hay IA disponible, usar fallback simple
                        formatted_data_text = _format_data_fallback_simple(
                            query_data, 
                            result.get('query_type', ''),
                            result.get('message', '')
                        )
                    
                    # Combinar el mensaje inicial con los datos formateados
                    if formatted_data_text:
                        initial_msg = result.get('message', '')
                        if initial_msg and formatted_data_text != initial_msg:
                            # Si el mensaje formateado ya incluye el inicial, usar solo el formateado
                            if initial_msg in formatted_data_text:
                                result['message'] = formatted_data_text
                            else:
                                result['message'] = f"{initial_msg}\n\n{formatted_data_text}"
                        else:
                            result['message'] = formatted_data_text
                    
                    # IMPORTANTE: Limpiar el campo 'data' para que el frontend no muestre JSON crudo
                    # O mantenerlo pero el mensaje ya tiene todo formateado
                    # result['data'] = None  # Opcional: eliminar datos crudos si el mensaje ya los incluye
                    
                    print(f"✅ Resultados formateados a lenguaje natural")
                except Exception as e:
                    print(f"⚠️  Error formateando resultados: {e}")
                    import traceback
                    traceback.print_exc()
                    # Usar fallback simple si todo falla
                    try:
                        result['message'] = _format_data_fallback_simple(
                            query_data,
                            result.get('query_type', ''),
                            result.get('message', '')
                        )
                    except:
                        pass  # Si incluso el fallback falla, mantener el mensaje original
        
        # Agregar información adicional
        result['confidence'] = intent_data.get('confidence', 0.0)
        # Manejar intent que puede ser enum o string
        intent = intent_data.get('intent')
        if intent:
            if hasattr(intent, 'value'):
                result['intent'] = intent.value  # Es un IntentType enum
            else:
                result['intent'] = str(intent)  # Es un string
        else:
            result['intent'] = None
        result['user_name'] = user_name
        result['user_role'] = user_role
        
        # Serializar respuesta
        response_serializer = ChatResponseSerializer(result)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error en chatbot chat endpoint: {e}")
        print(f"   Traceback completo:\n{error_trace}")
        return Response(
            {
                'success': False,
                'message': f'Hola {user_name}, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.',
                'query_type': 'error',
                'data': None,
                'error_details': str(e) if settings.DEBUG else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def help(request):
    """
    Endpoint para obtener ayuda y ejemplos de uso del chatbot
    
    GET /api/chatbot/help/
    """
    try:
        help_result = query_service._get_help_message()
        response_serializer = ChatResponseSerializer(help_result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {
                'success': False,
                'message': f'Error: {str(e)}',
                'query_type': 'error',
                'data': None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
