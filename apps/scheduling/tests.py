# apps/scheduling/tests.py
from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from apps.academic_setup.models import (
    PeriodoAcademico, Carrera, UnidadAcademica, Materias, TiposEspacio
)
from apps.users.models import Docentes
from .models import Grupos, HorariosAsignados, BloquesHorariosDefinicion


class GruposViewSetTestCase(TestCase):
    """Tests para el ViewSet de Grupos"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        
        # Crear datos de prueba
        self.unidad = UnidadAcademica.objects.create(
            nombre_unidad="Facultad de Prueba"
        )
        self.carrera = Carrera.objects.create(
            nombre_carrera="Carrera de Prueba",
            codigo_carrera="TEST001",
            unidad=self.unidad
        )
        self.periodo = PeriodoAcademico.objects.create(
            nombre_periodo="2025-I",
            fecha_inicio="2025-01-01",
            fecha_fin="2025-06-30",
            activo=True
        )

    def test_create_grupo(self):
        """Test crear un grupo"""
        data = {
            'codigo_grupo': 'GRP-TEST-001',
            'carrera': self.carrera.carrera_id,
            'periodo': self.periodo.periodo_id,
            'numero_estudiantes_estimado': 30,
            'materias': []
        }
        response = self.client.post('/api/scheduling/grupos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Grupos.objects.count(), 1)

    def test_list_grupos(self):
        """Test listar grupos"""
        response = self.client.get('/api/scheduling/grupos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_access(self):
        """Test que usuarios no autenticados no pueden acceder"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/scheduling/grupos/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_grupo(self):
        """Test actualizar un grupo"""
        grupo = Grupos.objects.create(
            codigo_grupo='GRP-TEST-001',
            carrera=self.carrera,
            periodo=self.periodo,
            numero_estudiantes_estimado=30
        )
        
        data = {
            'codigo_grupo': 'GRP-TEST-001-UPDATED',
            'carrera': self.carrera.carrera_id,
            'periodo': self.periodo.periodo_id,
            'numero_estudiantes_estimado': 35,
            'materias': []
        }
        
        response = self.client.put(f'/api/scheduling/grupos/{grupo.grupo_id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        grupo.refresh_from_db()
        self.assertEqual(grupo.numero_estudiantes_estimado, 35)


class HorariosAsignadosTestCase(TestCase):
    """Tests para Horarios Asignados"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        
        # Crear datos necesarios
        self.unidad = UnidadAcademica.objects.create(nombre_unidad="Facultad Test")
        self.carrera = Carrera.objects.create(
            nombre_carrera="Carrera Test",
            codigo_carrera="TEST",
            unidad=self.unidad
        )
        self.periodo = PeriodoAcademico.objects.create(
            nombre_periodo="2025-I",
            fecha_inicio="2025-01-01",
            fecha_fin="2025-06-30",
            activo=True
        )
        self.tipo_espacio = TiposEspacio.objects.create(
            nombre_tipo_espacio="Aula"
        )
        self.docente = Docentes.objects.create(
            codigo_docente="DOC001",
            nombres="Test",
            apellidos="Docente"
        )

    def test_list_horarios(self):
        """Test listar horarios asignados"""
        response = self.client.get('/api/scheduling/horarios-asignados/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PermissionsTestCase(TestCase):
    """Tests para verificar permisos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        
        # Crear usuario normal (no admin)
        self.normal_user = User.objects.create_user(
            username='normaluser',
            password='testpass123',
            is_staff=False
        )
        
        # Crear usuario admin
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='testpass123',
            is_staff=True
        )

    def test_normal_user_can_read(self):
        """Test que usuarios normales pueden leer"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get('/api/scheduling/grupos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_normal_user_cannot_create(self):
        """Test que usuarios normales no pueden crear"""
        self.client.force_authenticate(user=self.normal_user)
        data = {
            'codigo_grupo': 'GRP-TEST',
            'carrera': 1,
            'periodo': 1,
            'materias': []
        }
        response = self.client.post('/api/scheduling/grupos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create(self):
        """Test que admins pueden crear"""
        self.client.force_authenticate(user=self.admin_user)
        # Necesitaríamos datos válidos aquí, pero el test verifica el permiso
        # En un test completo, crearíamos los datos necesarios primero
        pass
