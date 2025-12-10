# apps/academic_setup/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import (
    UnidadAcademica, Carrera, PeriodoAcademico, TiposEspacio, EspaciosFisicos,
    Especialidades, Materias, CarreraMaterias, MateriaEspecialidadesRequeridas,
    TipoUnidadAcademica, Ciclo, Seccion
)
# Importación del modelo y serializador de la otra app
from apps.scheduling.models import Grupos
from apps.scheduling.serializers import GruposSerializer
from apps.scheduling.service.schedule_generator import ScheduleGeneratorService
from .services.bulk_import import BulkImportService
from .tasks import process_bulk_import_task
from rest_framework.parsers import MultiPartParser, FormParser
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid

def save_temp_file(file):
    # Save file to a temp location accessible by workers
    ext = os.path.splitext(file.name)[1]
    filename = f"temp_imports/{uuid.uuid4()}{ext}"
    path = default_storage.save(filename, ContentFile(file.read()))
    return default_storage.path(path)


from .serializers import (
    UnidadAcademicaSerializer, CarreraSerializer, PeriodoAcademicoSerializer,
    TiposEspacioSerializer, EspaciosFisicosSerializer, EspecialidadesSerializer,
    MateriasSerializer, CarreraMateriasSerializer, MateriaEspecialidadesRequeridasSerializer,
    TipoUnidadAcademicaSerializer, CicloSerializer, SeccionSerializer
)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

# Nuevo ViewSet para TipoUnidadAcademica
class TipoUnidadAcademicaViewSet(viewsets.ModelViewSet):
    queryset = TipoUnidadAcademica.objects.all()
    serializer_class = TipoUnidadAcademicaSerializer
    permission_classes = [AllowAny] # Ajusta los permisos según tu sistema de autenticación

# Modificado: UnidadAcademicaViewSet para incluir el tipo_unidad
class UnidadAcademicaViewSet(viewsets.ModelViewSet):
    queryset = UnidadAcademica.objects.select_related('tipo_unidad').all()
    serializer_class = UnidadAcademicaSerializer
    permission_classes = [AllowAny] # Ajusta los permisos

    # Permite filtrar ciclos por carrera_id: /api/academic_setup/ciclos/?carrera_id=X
    def get_queryset(self):
        queryset = super().get_queryset()
        carrera_id = self.request.query_params.get('carrera_id')
        if carrera_id:
            queryset = queryset.filter(carrera_id=carrera_id)
        return queryset

    @action(detail=True, methods=['post'], url_path='generar-horarios')
    def generar_horarios_masivos(self, request, pk=None):
        """
        Dispara la generación masiva de horarios para todos los grupos
        asociados a este ciclo en un período académico específico.
        """
        ciclo = self.get_object()
        periodo_id = request.data.get('periodo_id')

        if not periodo_id:
            return Response(
                {"error": "Se requiere el 'periodo_id' en el cuerpo de la petición."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            periodo = PeriodoAcademico.objects.get(pk=periodo_id)
        except PeriodoAcademico.DoesNotExist:
            return Response(
                {"error": f"El período académico con id {periodo_id} no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Instanciar el servicio con el período correcto
        generator = ScheduleGeneratorService(periodo=periodo)
        
        # Llamar al método de generación masiva por ciclo
        resultado = generator.generar_horarios_para_ciclo(ciclo_id=ciclo.ciclo_id)

        if "error" in resultado or "warning" in resultado:
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

        return Response(resultado, status=status.HTTP_200_OK)

# Nuevo ViewSet para Ciclo
class CicloViewSet(viewsets.ModelViewSet):
    queryset = Ciclo.objects.select_related('carrera').all()
    serializer_class = CicloSerializer
    permission_classes = [AllowAny] # Ajusta los permisos
    pagination_class = None # Deshabilitar paginación para este ViewSet

    # Permite filtrar ciclos por carrera_id: /api/academic_setup/ciclos/?carrera_id=X
    def get_queryset(self):
        queryset = super().get_queryset()
        carrera_id = self.request.query_params.get('carrera_id')
        print(f"Buscando ciclos para carrera_id: {carrera_id}") # <-- DEBUG
        if carrera_id:
            queryset = queryset.filter(carrera_id=carrera_id)
        print(f"Encontrados {queryset.count()} ciclos.") # <-- DEBUG
        return queryset

    @action(detail=True, methods=['post'], url_path='generar-horarios')
    def generar_horarios_masivos(self, request, pk=None):
        """
        Dispara la generación masiva de horarios para todos los grupos
        asociados a este ciclo en un período académico específico.
        """
        ciclo = self.get_object()
        periodo_id = request.data.get('periodo_id')

        if not periodo_id:
            return Response(
                {"error": "Se requiere el 'periodo_id' en el cuerpo de la petición."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            periodo = PeriodoAcademico.objects.get(pk=periodo_id)
        except PeriodoAcademico.DoesNotExist:
            return Response(
                {"error": f"El período académico con id {periodo_id} no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Instanciar el servicio con el período correcto
        generator = ScheduleGeneratorService(periodo=periodo)
        
        # Llamar al método de generación masiva por ciclo
        resultado = generator.generar_horarios_para_ciclo(ciclo_id=ciclo.ciclo_id)

        if "error" in resultado or "warning" in resultado:
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

        return Response(resultado, status=status.HTTP_200_OK)

# Nuevo ViewSet para Seccion
class SeccionViewSet(viewsets.ModelViewSet):
    # Utilizamos '__' para acceder a campos de modelos relacionados (ciclo y carrera a través del ciclo)
    queryset = Seccion.objects.select_related('ciclo__carrera').all()
    serializer_class = SeccionSerializer
    permission_classes = [AllowAny] # Ajusta los permisos

    # Permite filtrar secciones por ciclo_id o carrera_id:
    # /api/academic_setup/secciones/?ciclo_id=X
    # /api/academic_setup/secciones/?carrera_id=Y
    def get_queryset(self):
        queryset = super().get_queryset()
        ciclo_id = self.request.query_params.get('ciclo_id')
        carrera_id = self.request.query_params.get('carrera_id')
        if ciclo_id:
            queryset = queryset.filter(ciclo_id=ciclo_id)
        if carrera_id:
            queryset = queryset.filter(ciclo__carrera_id=carrera_id)
        return queryset

# Modificado: CarreraMateriasViewSet (si ajustaste el modelo CarreraMaterias)
class CarreraMateriasViewSet(viewsets.ModelViewSet):
    # Asegúrate de incluir 'ciclo' en el select_related si lo añadiste a CarreraMaterias
    queryset = CarreraMaterias.objects.select_related('carrera', 'materia', 'ciclo').all()
    serializer_class = CarreraMateriasSerializer
    permission_classes = [AllowAny] # Ajusta los permisos

    # Opcional: Filtrar por carrera, materia o ciclo
    def get_queryset(self):
        queryset = super().get_queryset().order_by('id')
        carrera_id = self.request.query_params.get('carrera_id')
        materia_id = self.request.query_params.get('materia_id')
        ciclo_id = self.request.query_params.get('ciclo_id')
        if carrera_id:
            queryset = queryset.filter(carrera_id=carrera_id)
        if materia_id:
            queryset = queryset.filter(materia_id=materia_id)
        if ciclo_id:
            queryset = queryset.filter(ciclo_id=ciclo_id)
        return queryset

# Los ViewSets existentes (sin cambios en la lógica, solo para completitud)
class CarreraViewSet(viewsets.ModelViewSet):
    queryset = Carrera.objects.select_related('unidad').all()
    serializer_class = CarreraSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['unidad']



    @action(detail=False, methods=['post'], url_path='cargar-excel', parser_classes=[MultiPartParser, FormParser])
    def cargar_excel(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            file_path = save_temp_file(file)
            task = process_bulk_import_task.delay(file_path, 'carreras', request.user.id if request.user.is_authenticated else None)
            return Response({'message': 'Importación iniciada', 'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='materias')
    def materias(self, request, pk=None):
        """
        Devuelve todas las materias asociadas a una carrera específica.
        Permite filtrar por ciclo_id opcionalmente.
        Ej: /api/academic-setup/carreras/1/materias/?ciclo_id=2
        """
        carrera = self.get_object()
        # Obtenemos las relaciones CarreraMaterias para esta carrera
        carrera_materias_qs = CarreraMaterias.objects.filter(carrera=carrera).select_related('materia', 'ciclo')

        # Filtro opcional por ciclo
        ciclo_id = request.query_params.get('ciclo_id')
        if ciclo_id:
            carrera_materias_qs = carrera_materias_qs.filter(ciclo_id=ciclo_id)

        # Extraemos los IDs de las materias
        materia_ids = [cm.materia.materia_id for cm in carrera_materias_qs]
        # Creamos un queryset de Materias
        materias_queryset = Materias.objects.filter(materia_id__in=materia_ids).prefetch_related('materiaespecialidadesrequeridas_set__especialidad')

        # Aplicamos la paginación al queryset
        page = self.paginate_queryset(materias_queryset)
        if page is not None:
            serializer = MateriasSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback por si la paginación no está activa
        serializer = MateriasSerializer(materias_queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='crear-grupos-masivos')
    def crear_grupos_masivos(self, request, pk=None):
        """
        Crea múltiples Grupos (de la app scheduling) para una carrera,
        basado en un ciclo y una lista de nombres de sección.
        """
        carrera = self.get_object()
        periodo_id = request.data.get('periodo_id')
        ciclo_id = request.data.get('ciclo_id')
        secciones = request.data.get('secciones') # Espera una lista: ["A", "B", "C"]

        if not all([periodo_id, ciclo_id, secciones]):
            return Response(
                {"error": "Se requiere 'periodo_id', 'ciclo_id' y 'secciones'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            periodo = PeriodoAcademico.objects.get(pk=periodo_id)
            ciclo_obj = Ciclo.objects.get(pk=ciclo_id, carrera=carrera)
        except (PeriodoAcademico.DoesNotExist, Ciclo.DoesNotExist):
            return Response(
                {"error": "El período o el ciclo especificado no existen o no pertenecen a esta carrera."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 1. Obtener todas las materias para ese ciclo/carrera
        materias_del_ciclo = Materias.objects.filter(carreramaterias__carrera=carrera, carreramaterias__ciclo=ciclo_obj)
        if not materias_del_ciclo.exists():
            return Response(
                {"warning": f"No hay materias asignadas al ciclo {ciclo_obj.orden} para la carrera {carrera.nombre_carrera}."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Iterar y crear los grupos
        grupos_creados = []
        for seccion_nombre in secciones:
            codigo_grupo = f"{carrera.codigo_carrera}-{ciclo_obj.orden}-{seccion_nombre}"
            
            # Usamos get_or_create para evitar duplicados si se llama dos veces
            grupo, created = Grupos.objects.get_or_create(
                codigo_grupo=codigo_grupo,
                periodo=periodo,
                defaults={
                    'carrera': carrera,
                    'ciclo_semestral': ciclo_obj.orden,
                    # Aquí podrías añadir otros valores por defecto si los necesitas
                }
            )

            if created:
                # Asignamos las materias al grupo recién creado
                grupo.materias.set(materias_del_ciclo)
                grupos_creados.append(GruposSerializer(grupo).data)

        return Response(
            {"message": f"{len(grupos_creados)} grupos creados exitosamente.", "grupos": grupos_creados},
            status=status.HTTP_201_CREATED
        )

class PeriodoAcademicoViewSet(viewsets.ModelViewSet):
    queryset = PeriodoAcademico.objects.all().order_by('-fecha_inicio')
    serializer_class = PeriodoAcademicoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activo']

class TiposEspacioViewSet(viewsets.ModelViewSet):
    queryset = TiposEspacio.objects.all()
    serializer_class = TiposEspacioSerializer
    permission_classes = [AllowAny]

class EspaciosFisicosPagination(PageNumberPagination):
    page_size = 100  # Valor por defecto aumentado
    page_size_query_param = 'page_size'
    max_page_size = 500

class EspaciosFisicosViewSet(viewsets.ModelViewSet):
    queryset = EspaciosFisicos.objects.select_related('tipo_espacio', 'unidad').all()
    serializer_class = EspaciosFisicosSerializer
    permission_classes = [AllowAny]
    pagination_class = EspaciosFisicosPagination


class EspecialidadesViewSet(viewsets.ModelViewSet):
    queryset = Especialidades.objects.all()
    serializer_class = EspecialidadesSerializer
    permission_classes = [AllowAny]

class MateriasViewSet(viewsets.ModelViewSet):
    queryset = Materias.objects.all()
    serializer_class = MateriasSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['estado']

class MateriaEspecialidadesRequeridasViewSet(viewsets.ModelViewSet):
    queryset = MateriaEspecialidadesRequeridas.objects.select_related('materia', 'especialidad').all()
    serializer_class = MateriaEspecialidadesRequeridasSerializer
    permission_classes = [AllowAny]