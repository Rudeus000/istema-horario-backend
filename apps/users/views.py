# apps/users/views.py
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView

# Importaciones de tus modelos locales:
from .models import Docentes, Roles, DocenteEspecialidades
from apps.scheduling.models import HorariosAsignados, DisponibilidadDocentes
from apps.academic_setup.models import MateriaEspecialidadesRequeridas

# Importaciones de tus serializers locales:
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    DocentesSerializer,
    RolesSerializer,
    GroupSerializer,
    CustomTokenObtainPairSerializer,
    DocenteEspecialidadesSimpleSerializer,
    UserUpdateSerializer,
)

from apps.academic_setup.tasks import process_bulk_import_task
from rest_framework.parsers import MultiPartParser, FormParser
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid

def save_temp_file(file):
    ext = os.path.splitext(file.name)[1]
    filename = f"temp_imports/{uuid.uuid4()}{ext}"
    path = default_storage.save(filename, ContentFile(file.read()))
    return default_storage.path(path)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class RolesViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer
    permission_classes = [AllowAny]

class DocentesViewSet(viewsets.ModelViewSet):
    queryset = Docentes.objects.select_related('usuario', 'unidad_principal').prefetch_related('especialidades').all()
    serializer_class = DocentesSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()

        unidad_id = self.request.query_params.get('unidad_id')
        especialidad_id = self.request.query_params.get('especialidad_id')
        materia_id = self.request.query_params.get('materia_id')
        periodo_id = self.request.query_params.get('periodo_id')
        dia_semana = self.request.query_params.get('dia_semana')
        bloque_id = self.request.query_params.get('bloque_id')
        
        if unidad_id:
            queryset = queryset.filter(unidad_principal_id=unidad_id)
        if especialidad_id:
            queryset = queryset.filter(especialidades__especialidad_id=especialidad_id).distinct()

        if materia_id:
            try:
                especialidades_requeridas_ids = MateriaEspecialidadesRequeridas.objects.filter(
                    materia_id=materia_id
                ).values_list('especialidad_id', flat=True)

                if especialidades_requeridas_ids.exists():
                    queryset = queryset.filter(
                        especialidades__especialidad_id__in=especialidades_requeridas_ids
                    ).distinct()
            except (ValueError, TypeError):
                pass

        if periodo_id and dia_semana and bloque_id:
            docentes_ocupados = HorariosAsignados.objects.filter(
                periodo_id=periodo_id,
                dia_semana=dia_semana,
                bloque_horario_id=bloque_id
            ).values_list('docente_id', flat=True)

            docentes_con_disponibilidad = DisponibilidadDocentes.objects.filter(
                periodo_id=periodo_id,
                dia_semana=dia_semana,
                bloque_horario_id=bloque_id,
                esta_disponible=True
            ).values_list('docente_id', flat=True)
            
            queryset = queryset.filter(
                docente_id__in=docentes_con_disponibilidad
            ).exclude(
                docente_id__in=docentes_ocupados
            )

        return queryset

    @action(detail=False, methods=['post'], url_path='cargar-excel', parser_classes=[MultiPartParser, FormParser])
    def cargar_excel(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            file_path = save_temp_file(file)
            task = process_bulk_import_task.delay(file_path, 'docentes', request.user.id if request.user.is_authenticated else None)
            return Response({'message': 'Importación iniciada', 'task_id': task.id}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class DocenteEspecialidadesViewSet(viewsets.ModelViewSet):
    queryset = DocenteEspecialidades.objects.all()
    serializer_class = DocenteEspecialidadesSimpleSerializer
    permission_classes = [AllowAny]