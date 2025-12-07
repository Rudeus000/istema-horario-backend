#apps/users/views.py
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

# Importaciones de rest_framework_simplejwt:
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView # <-- TokenObtainPairView sí se importa de views

# Importaciones de tus modelos locales:
from .models import Docentes, Roles, DocenteEspecialidades # Aquí sí importas Roles y DocenteEspecialidades

# Importaciones de tus serializers locales:
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    DocentesSerializer,
    RolesSerializer,
    GroupSerializer,
    CustomTokenObtainPairSerializer, # <-- ¡Este es el nombre correcto!
    DocenteEspecialidadesSimpleSerializer,
    UserUpdateSerializer, # <--- importar el nuevo serializer
)

# Importar modelos necesarios para el filtrado avanzado
from apps.scheduling.models import HorariosAsignados, DisponibilidadDocentes
from apps.academic_setup.models import MateriaEspecialidadesRequeridas
from django.db.models import Q

# from ..permissions import IsAdminOrSelf # Permiso personalizado

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Solo admins pueden gestionar usuarios

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
            # Podrías retornar un token aquí también si quieres login inmediato
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
    permission_classes = [permissions.IsAuthenticated]

class DocentesViewSet(viewsets.ModelViewSet):
    queryset = Docentes.objects.select_related('usuario', 'unidad_principal').prefetch_related('especialidades').all()
    serializer_class = DocentesSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()

        # Parámetros para filtrado simple
        unidad_id = self.request.query_params.get('unidad_id')
        especialidad_id = self.request.query_params.get('especialidad_id')

        # Parámetros para filtrado por materia (cualificación)
        materia_id = self.request.query_params.get('materia_id')

        # Parámetros para filtrado de disponibilidad
        periodo_id = self.request.query_params.get('periodo_id')
        dia_semana = self.request.query_params.get('dia_semana')
        bloque_id = self.request.query_params.get('bloque_id')
        
        if unidad_id:
            queryset = queryset.filter(unidad_principal_id=unidad_id)
        if especialidad_id:
            queryset = queryset.filter(especialidades__especialidad_id=especialidad_id).distinct()

        # --- Lógica de filtrado por cualificación de materia ---
        if materia_id:
            try:
                # 1. Obtener las especialidades requeridas para la materia
                especialidades_requeridas_ids = MateriaEspecialidadesRequeridas.objects.filter(
                    materia_id=materia_id
                ).values_list('especialidad_id', flat=True)

                # 2. Si hay especialidades requeridas, filtrar docentes que tengan al menos una de ellas
                if especialidades_requeridas_ids.exists():
                    queryset = queryset.filter(
                        especialidades__especialidad_id__in=especialidades_requeridas_ids
                    ).distinct()
                # Opcional: si la materia no requiere especialidad, no se filtra y se devuelven todos.
                # Si se quisiera que no devuelva ninguno, se añadiría: else: return queryset.none()
            except (ValueError, TypeError):
                # Ignorar si el materia_id no es válido
                pass

        # --- Lógica de filtrado avanzado para disponibilidad ---
        if periodo_id and dia_semana and bloque_id:
            # 1. Docentes que YA tienen una clase asignada en ese bloque
            docentes_ocupados = HorariosAsignados.objects.filter(
                periodo_id=periodo_id,
                dia_semana=dia_semana,
                bloque_horario_id=bloque_id
            ).values_list('docente_id', flat=True)

            # 2. Docentes que SÍ han registrado disponibilidad para ese bloque
            docentes_con_disponibilidad = DisponibilidadDocentes.objects.filter(
                periodo_id=periodo_id,
                dia_semana=dia_semana,
                bloque_horario_id=bloque_id,
                esta_disponible=True
            ).values_list('docente_id', flat=True)
            
            # Aplicar filtros al queryset
            queryset = queryset.filter(
                docente_id__in=docentes_con_disponibilidad
            ).exclude(
                docente_id__in=docentes_ocupados
            )

        return queryset

# Para login y refresh de tokens
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    pass

class DocenteEspecialidadesViewSet(viewsets.ModelViewSet):
    queryset = DocenteEspecialidades.objects.all()
    serializer_class = DocenteEspecialidadesSimpleSerializer
    permission_classes = [AllowAny]