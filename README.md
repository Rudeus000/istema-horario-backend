# Sistema de Gestión de Horarios - La Pontificia

Sistema completo para la gestión y generación automática de horarios académicos desarrollado con Django REST Framework, Celery y Redis.

## 📋 Tabla de Contenidos

- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución del Sistema](#ejecución-del-sistema)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Comandos Útiles](#comandos-útiles)

## 🏗️ Arquitectura del Sistema

El sistema utiliza una **arquitectura distribuida** basada en microservicios con las siguientes componentes:

### Componentes Principales

```
┌─────────────────┐
│   Frontend      │  (React/TypeScript)
│   (Cliente)     │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼─────────────────────────────────────┐
│         Django REST Framework API            │
│  ┌────────────────────────────────────────┐ │
│  │  - Autenticación JWT                   │ │
│  │  - Endpoints REST                      │ │
│  │  - Validación de datos                │ │
│  └────────────────────────────────────────┘ │
└────────┬────────────────────────────────────┘
         │
         ├─────────────────┬──────────────────┐
         │                 │                  │
┌────────▼────────┐  ┌───▼──────────┐  ┌───▼──────────┐
│   PostgreSQL    │  │    Redis      │  │   Celery     │
│   (Base Datos)  │  │  (Cache/Broker)│  │  (Workers)   │
└─────────────────┘  └───────────────┘  └──────────────┘
```

### Arquitectura Distribuida

El sistema implementa una **arquitectura distribuida** con:

1. **Django REST Framework**: API REST para comunicación con el frontend
2. **PostgreSQL**: Base de datos relacional para persistencia de datos
3. **Redis**: 
   - Cache para mejorar rendimiento
   - Broker de mensajes para Celery
   - Almacenamiento de sesiones
4. **Celery**: Sistema de tareas asíncronas distribuidas con múltiples colas:
   - **Cola `horarios`**: Tareas pesadas de generación de horarios
   - **Cola `metricas`**: Actualización de métricas del dashboard
   - **Cola `validacion`**: Validación de conflictos
   - **Cola `auditoria`**: Registro de eventos y logs

### Características de la Arquitectura

- **Circuit Breaker**: Protección contra fallos en cascada
- **Métricas y Auditoría**: Sistema de monitoreo y registro de eventos
- **Load Balancing**: Distribución de carga mediante colas de Celery
- **Cache Inteligente**: Redis para optimizar consultas frecuentes
- **Autenticación JWT**: Tokens seguros para autenticación

## 📦 Requisitos

### Software Necesario

- **Python**: 3.11 o superior
- **PostgreSQL**: 12 o superior
- **Redis**: 6.0 o superior
- **Git**: Para clonar el repositorio

### Dependencias Python

Todas las dependencias están listadas en `requirements.txt`:
- Django 5.2.1
- Django REST Framework 3.16.0
- Celery 5.5.2
- Redis 6.1.0
- PostgreSQL (psycopg2)
- Y más...

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Rudeus000/istema-horario-backend.git
cd istema-horario-backend
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos PostgreSQL

Crear una base de datos en PostgreSQL:

```sql
CREATE DATABASE Sistemaponti;
CREATE USER tu_usuario WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE Sistemaponti TO tu_usuario;
```

### 5. Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Django
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos
DB_NAME=Sistemaponti
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

### 6. Aplicar Migraciones

```bash
python manage.py migrate
```

### 7. Crear Superusuario (Opcional)

```bash
python manage.py createsuperuser
```

## ⚙️ Configuración

### Configuración de Redis

Redis debe estar ejecutándose antes de iniciar el sistema:

**Windows:**
```bash
# Si Redis está instalado en la ruta predeterminada
"C:\Program Files\Redis\redis-server.exe" --port 6379
```

**Linux/Mac:**
```bash
redis-server --port 6379
```

### Configuración de Celery

El sistema está configurado para usar múltiples colas de Celery:

- **DB 0**: Broker y Result Backend de Celery
- **DB 1**: Cache de Django y sesiones

## 🏃 Ejecución del Sistema

### Opción 1: Ejecución Manual (Recomendado para Desarrollo)

#### Paso 1: Iniciar Redis

**Windows:**
```bash
"C:\Program Files\Redis\redis-server.exe" --port 6379
```

**Linux/Mac:**
```bash
redis-server
```

#### Paso 2: Iniciar Celery Worker

En una terminal separada:

```bash
# Worker para todas las colas
celery -A la_pontificia_horarios worker --loglevel=info

# O workers específicos por cola (recomendado para producción)
celery -A la_pontificia_horarios worker --loglevel=info --queues=horarios --concurrency=2
celery -A la_pontificia_horarios worker --loglevel=info --queues=metricas --concurrency=4
celery -A la_pontificia_horarios worker --loglevel=info --queues=validacion --concurrency=4
celery -A la_pontificia_horarios worker --loglevel=info --queues=auditoria --concurrency=2
```

#### Paso 3: Iniciar Django Server

En otra terminal:

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

#### Paso 4: (Opcional) Monitoreo con Flower

Para monitorear las tareas de Celery:

```bash
celery -A la_pontificia_horarios flower
```

Acceder a: `http://localhost:5555`

### Opción 2: Verificar Estado

```bash
# Verificar Redis
redis-cli ping  # Debe responder: PONG

# Verificar Celery
celery -A la_pontificia_horarios inspect active
```

## 📁 Estructura del Proyecto

```
istema-horario-backend/
├── apps/
│   ├── academic_setup/          # Configuración académica
│   │   ├── models.py           # Modelos: Unidades, Carreras, Materias, etc.
│   │   ├── views.py            # Vistas API
│   │   ├── serializers.py     # Serializadores DRF
│   │   └── management/
│   │       └── commands/       # Comandos de seed
│   │
│   ├── scheduling/             # Sistema de horarios
│   │   ├── models.py          # Modelos: Grupos, Horarios, Disponibilidad
│   │   ├── views.py           # Vistas API
│   │   ├── tasks.py           # Tareas asíncronas Celery
│   │   ├── service/           # Lógica de negocio
│   │   │   ├── schedule_generator.py    # Generador de horarios
│   │   │   └── conflict_validator.py   # Validador de conflictos
│   │   ├── audit.py           # Sistema de auditoría
│   │   ├── metrics.py         # Sistema de métricas
│   │   ├── circuit_breaker.py # Circuit breaker pattern
│   │   └── events.py          # Eventos del sistema
│   │
│   └── users/                 # Gestión de usuarios
│       ├── models.py          # Modelos: Usuarios, Docentes
│       ├── views.py           # Vistas API
│       └── serializers.py    # Serializadores DRF
│
├── la_pontificia_horarios/    # Configuración Django
│   ├── settings.py           # Configuración principal
│   ├── urls.py               # URLs principales
│   ├── celery.py             # Configuración Celery
│   └── wsgi.py               # WSGI para producción
│
├── manage.py                 # Script de gestión Django
├── requirements.txt          # Dependencias Python
└── .env                      # Variables de entorno (no en git)
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2.1**: Framework web Python
- **Django REST Framework 3.16.0**: API REST
- **Django REST Framework Simple JWT**: Autenticación JWT
- **Celery 5.5.2**: Tareas asíncronas distribuidas
- **Redis 6.1.0**: Cache y broker de mensajes
- **PostgreSQL**: Base de datos relacional
- **psycopg2**: Driver PostgreSQL para Python

### Herramientas de Desarrollo
- **Flower**: Monitoreo de Celery
- **Gunicorn**: Servidor WSGI para producción
- **Faker**: Generación de datos de prueba
- **python-decouple**: Gestión de variables de entorno

### Patrones y Arquitectura
- **Circuit Breaker Pattern**: Protección contra fallos
- **Event-Driven Architecture**: Sistema de eventos
- **Microservices**: Arquitectura distribuida
- **Load Balancing**: Distribución de carga con colas

## 📝 Comandos Útiles

### Gestión de Base de Datos

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### Seed de Datos

```bash
# Datos mínimos para pruebas
python manage.py seed_minimos

# Datos completos de La Pontificia
python manage.py seed_la_pontificia

# Crear bloques horarios
python manage.py crear_bloques_horarios

# Crear docentes masivos
python manage.py seed_docentes_masivos --periodo 1 --unidad 1
```

### Celery

```bash
# Iniciar worker
celery -A la_pontificia_horarios worker --loglevel=info

# Monitorear tareas
celery -A la_pontificia_horarios inspect active

# Ver estadísticas
celery -A la_pontificia_horarios inspect stats

# Flower (monitoreo web)
celery -A la_pontificia_horarios flower
```

### Django Shell

```bash
# Abrir shell interactivo
python manage.py shell

# Ejemplo en shell:
from apps.academic_setup.models import PeriodoAcademico
periodos = PeriodoAcademico.objects.all()
```

## 🔐 Autenticación

El sistema utiliza **JWT (JSON Web Tokens)** para autenticación:

1. **Login**: `POST /auth/login/` - Obtener tokens
2. **Refresh**: `POST /auth/refresh/` - Renovar token de acceso
3. **Uso**: Incluir token en header: `Authorization: Bearer <token>`

## 📊 Endpoints Principales

- `/api/academic/` - Configuración académica
- `/api/users/` - Gestión de usuarios y docentes
- `/api/scheduling/` - Gestión de horarios
- `/admin/` - Panel de administración Django

## 🐛 Solución de Problemas

### Redis no responde
```bash
# Verificar si está ejecutándose
redis-cli ping

# Reiniciar Redis (Windows)
taskkill /f /im redis-server.exe
"C:\Program Files\Redis\redis-server.exe" --port 6379
```

### Celery no conecta
```bash
# Verificar configuración
python manage.py shell
from django.conf import settings
print(settings.CELERY_BROKER_URL)
```

### Error de migraciones
```bash
# Resetear migraciones (¡CUIDADO: elimina datos!)
python manage.py migrate --run-syncdb
```

## 📄 Licencia

Este proyecto es privado y pertenece a La Pontificia.

## 👥 Contribuidores

- Rudeus000
- AndreMendezCisneros

---

**Versión**: 1.0  
**Última actualización**: Diciembre 2025

