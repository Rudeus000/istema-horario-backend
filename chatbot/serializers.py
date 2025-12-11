"""
Serializers para el chatbot
"""
from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    """Serializer para mensajes del chatbot"""
    message = serializers.CharField(
        max_length=500,
        help_text="Mensaje del usuario en lenguaje natural"
    )
    conversation_id = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="ID de conversación para mantener contexto (opcional)"
    )


class ChatResponseSerializer(serializers.Serializer):
    """Serializer para respuestas del chatbot"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.JSONField(required=False, allow_null=True)
    query_type = serializers.CharField()
    confidence = serializers.FloatField(required=False, allow_null=True)
    count = serializers.IntegerField(required=False, allow_null=True)
    user_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    user_role = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    intent = serializers.CharField(required=False, allow_null=True, allow_blank=True)

