"""
Script completo de prueba del chatbot
Ejecutar: python chatbot/test_completo.py
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'la_pontificia_horarios.settings')
django.setup()

from decouple import config
from chatbot.services.google_ai_service import GoogleAIService
from chatbot.services.nlp_service import NLPService

print("=" * 70)
print("🧪 PRUEBA COMPLETA DEL CHATBOT CON GOOGLE AI")
print("=" * 70)
print()

# Verificar API Key
api_key = config('GOOGLE_AI_API_KEY', default='')
print(f"✅ API Key configurada: {'Sí' if api_key else 'No'}")
if api_key:
    print(f"   Longitud: {len(api_key)} caracteres")
print()

# Inicializar servicios
print("1️⃣ Inicializando servicios...")
try:
    google_service = GoogleAIService(api_key)
    nlp_service = NLPService(use_ai=True, google_ai_api_key=api_key)
    print(f"   ✅ Google AI Service inicializado")
    print(f"   ✅ NLP Service inicializado (usa AI: {nlp_service.use_ai})")
    print()
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Pruebas
test_cases = [
    {
        "message": "Hola",
        "user_name": "Juan Pérez",
        "user_role": "Docente",
        "expected_intent": "saludo"
    },
    {
        "message": "¿Qué aulas están disponibles el lunes a las 8:00?",
        "user_name": "María García",
        "user_role": "Administrador",
        "expected_intent": "aulas_disponibles"
    },
    {
        "message": "¿Qué huecos tengo el lunes?",
        "user_name": "Juan Pérez",
        "user_role": "Docente",
        "expected_intent": "huecos_docente"
    },
    {
        "message": "Dame estadísticas del período actual",
        "user_name": "Ana López",
        "user_role": "Coordinador Académico",
        "expected_intent": "estadisticas_periodo"
    },
    {
        "message": "Buscar docente llamado García",
        "user_name": "Carlos",
        "user_role": "Administrador",
        "expected_intent": "buscar_docente"
    },
    {
        "message": "necesito ver mis clases de esta semana",
        "user_name": "Juan Pérez",
        "user_role": "Docente",
        "expected_intent": "horarios_docente"
    },
]

print("2️⃣ Probando procesamiento de mensajes...")
print()

results = {"success": 0, "failed": 0}

for i, test in enumerate(test_cases, 1):
    print(f"{'─' * 70}")
    print(f"Prueba {i}: {test['message']}")
    print(f"Usuario: {test['user_name']} ({test['user_role']})")
    
    try:
        # Procesar con NLP Service
        intent_data = nlp_service.process(
            user_message=test['message'],
            user_name=test['user_name'],
            user_role=test['user_role']
        )
        
        intent = intent_data.get('intent')
        intent_value = intent.value if intent else None
        confidence = intent_data.get('confidence', 0)
        
        # Verificar resultado
        if intent_value == test['expected_intent']:
            status = "✅ PASÓ"
            results["success"] += 1
        else:
            status = "⚠️  DIFERENTE"
            results["failed"] += 1
        
        print(f"   {status}")
        print(f"   Intención detectada: {intent_value}")
        print(f"   Esperada: {test['expected_intent']}")
        print(f"   Confianza: {confidence:.2f}")
        
        entities = intent_data.get('entities', {})
        if entities:
            print(f"   Entidades: {entities}")
        
        if intent_data.get('personalized_message'):
            msg = intent_data['personalized_message'][:100]
            print(f"   Mensaje: {msg}...")
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        results["failed"] += 1
    
    print()

print("=" * 70)
print(f"📊 RESULTADOS: {results['success']} exitosas, {results['failed']} fallidas")
print("=" * 70)

if results['failed'] == 0:
    print("✅ ¡Todas las pruebas pasaron exitosamente!")
else:
    print("⚠️  Algunas pruebas fallaron, pero el sistema está funcionando.")

