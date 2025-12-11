"""
Script de prueba para el chatbot
Ejecutar: python manage.py shell < chatbot/test_chatbot.py
O mejor: python -c "exec(open('chatbot/test_chatbot.py').read())"
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la_pontificia_horarios.settings')
django.setup()

from chatbot.services.nlp_service import NLPService
from chatbot.services.query_service import QueryService
from chatbot.services.google_ai_service import GoogleAIService
from decouple import config

print("=" * 60)
print("🧪 PRUEBA DEL CHATBOT CON GOOGLE AI")
print("=" * 60)
print()

# Verificar API Key
api_key = config('GOOGLE_AI_API_KEY', default='')
print(f"✅ API Key configurada: {'Sí' if api_key else 'No'}")
if api_key:
    print(f"   Longitud: {len(api_key)} caracteres")
print()

# Probar inicialización de servicios
print("1️⃣ Inicializando servicios...")
try:
    nlp_service = NLPService(use_ai=True, google_ai_api_key=api_key)
    query_service = QueryService()
    print(f"   ✅ NLP Service - Usa AI: {nlp_service.use_ai}")
    print(f"   ✅ Query Service - Inicializado")
    print()
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Pruebas de mensajes
test_messages = [
    {
        "message": "Hola",
        "user_name": "Juan Pérez",
        "user_role": "Docente",
        "description": "Saludo básico"
    },
    {
        "message": "¿Qué aulas están disponibles el lunes a las 8:00?",
        "user_name": "María García",
        "user_role": "Administrador",
        "description": "Consulta de aulas disponibles"
    },
    {
        "message": "¿Qué huecos tengo?",
        "user_name": "Juan Pérez",
        "user_role": "Docente",
        "description": "Consulta de huecos de docente (con 'mi')"
    },
    {
        "message": "Dame estadísticas del período actual",
        "user_name": "Ana López",
        "user_role": "Coordinador Académico",
        "description": "Estadísticas del período"
    },
]

print("2️⃣ Probando procesamiento de mensajes con Google AI...")
print()

for i, test in enumerate(test_messages, 1):
    print(f"--- Prueba {i}: {test['description']} ---")
    print(f"Mensaje: '{test['message']}'")
    print(f"Usuario: {test['user_name']} ({test['user_role']})")
    
    try:
        # Procesar mensaje
        intent_data = nlp_service.process(
            user_message=test['message'],
            user_name=test['user_name'],
            user_role=test['user_role']
        )
        
        print(f"✅ Intención detectada: {intent_data.get('intent').value if intent_data.get('intent') else 'N/A'}")
        print(f"   Confianza: {intent_data.get('confidence', 0):.2f}")
        print(f"   Entidades: {intent_data.get('entities', {})}")
        if intent_data.get('personalized_message'):
            print(f"   Mensaje personalizado: {intent_data['personalized_message'][:100]}...")
        
        # Ejecutar consulta (sin usuario real, solo para probar estructura)
        if intent_data.get('intent'):
            try:
                result = query_service.execute_query(
                    intent_data,
                    user=None,  # Sin usuario real para prueba
                    user_role=test['user_role']
                )
                print(f"✅ Consulta ejecutada: {result.get('query_type', 'N/A')}")
                print(f"   Éxito: {result.get('success', False)}")
                print(f"   Mensaje: {result.get('message', '')[:80]}...")
            except Exception as e:
                print(f"   ⚠️ Error en consulta (esperado sin DB): {str(e)[:60]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()

print("=" * 60)
print("✅ Pruebas completadas")
print("=" * 60)

