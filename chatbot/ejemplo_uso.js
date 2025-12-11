/**
 * Ejemplo de uso del Chatbot desde el Frontend
 * 
 * Este archivo muestra cómo integrar el chatbot en tu frontend React/Vue/etc.
 */

// Configuración
const API_BASE_URL = 'http://localhost:8000/api';
const CHATBOT_ENDPOINT = `${API_BASE_URL}/chatbot/chat`;

// Función para enviar mensaje al chatbot
async function enviarMensajeChatbot(mensaje, token) {
    try {
        const response = await fetch(CHATBOT_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({
                message: mensaje,
                conversation_id: '', // Opcional: para mantener contexto
            }),
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error al comunicarse con el chatbot:', error);
        throw error;
    }
}

// Ejemplo de uso en React
/*
import React, { useState } from 'react';

function ChatbotComponent() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const token = localStorage.getItem('authToken'); // Tu token JWT

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setInput('');
        setMessages([...messages, { type: 'user', text: userMessage }]);
        setLoading(true);

        try {
            const response = await enviarMensajeChatbot(userMessage, token);
            
            setMessages(prev => [
                ...prev,
                {
                    type: 'bot',
                    text: response.message,
                    data: response.data,
                    queryType: response.query_type,
                }
            ]);
        } catch (error) {
            setMessages(prev => [
                ...prev,
                {
                    type: 'error',
                    text: 'Error al comunicarse con el chatbot. Por favor intenta de nuevo.',
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chatbot-container">
            <div className="messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.type}`}>
                        <p>{msg.text}</p>
                        {msg.data && msg.data.length > 0 && (
                            <div className="data-display">
                                {/* Renderizar datos según queryType */}
                                {msg.queryType === 'aulas_disponibles' && (
                                    <ul>
                                        {msg.data.map(aula => (
                                            <li key={aula.id}>
                                                {aula.nombre} - {aula.tipo} 
                                                ({aula.capacidad} estudiantes)
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        )}
                    </div>
                ))}
                {loading && <div className="loading">Pensando...</div>}
            </div>
            
            <div className="input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Pregunta algo sobre el sistema..."
                />
                <button onClick={handleSend} disabled={loading}>
                    Enviar
                </button>
            </div>
        </div>
    );
}
*/

// Ejemplo de preguntas que puedes hacer:
const ejemplos = [
    "¿Qué aulas están disponibles el lunes a las 8:00?",
    "¿Qué docentes están libres los martes por la tarde?",
    "¿Qué horarios tiene el docente Juan Pérez?",
    "¿Qué clases hay en el aula A101?",
    "¿Qué tipos de aulas hay?",
    "Buscar docente llamado García",
    "Buscar aula A101",
    "Hola",
    "Ayuda",
];

export { enviarMensajeChatbot, ejemplos };

