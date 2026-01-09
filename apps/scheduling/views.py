# apps/scheduling/view.py
from django.db import models # <--- AÑADE O ASEGÚRATE QUE ESTA LÍNEA EXISTA

from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend # Para filtrado avanzado
from .models import Grupos, BloquesHorariosDefinicion, DisponibilidadDocentes, HorariosAsignados, ConfiguracionRestricciones, ScheduleAuditLog
from .tasks import generar_horarios_task # Importar la tarea Celery
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.exceptions import ValidationError, APIException

# Importar el servicio
from .service.schedule_generator import ScheduleGeneratorService # Asegúrate que la ruta sea correcta (service o services)
import logging
logger = logging.getLogger(__name__)

from .serializers import (
    GruposSerializer, BloquesHorariosDefinicionSerializer, DisponibilidadDocentesSerializer,
    HorariosAsignadosSerializer, ConfiguracionRestriccionesSerializer
)
# Importar servicios
from .service.schedule_generator import ScheduleGeneratorService
from .service.conflict_validator import ConflictValidatorService
from apps.academic_setup.models import PeriodoAcademico # Para la acción de generar
from .metrics import MetricsManager
from .audit import AuditManager

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import openpyxl
from django.db import transaction

class GruposViewSet(viewsets.ModelViewSet):
    queryset = Grupos.objects.select_related(
        'carrera', 'periodo', 'docente_asignado_directamente'
    ).prefetch_related('materias').all()
    serializer_class = GruposSerializer
    permission_classes = [permissions.AllowAny] # Temporalmente abierto para pruebas
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['carrera', 'periodo', 'ciclo_semestral', 'turno_preferente']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Obtener la instancia completa con prefetch para la respuesta
        instance = Grupos.objects.select_related(
            'carrera', 'periodo'
        ).prefetch_related('materias').get(pk=serializer.instance.pk)
        
        # Serializar la instancia completa para la respuesta
        response_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        print(f"[GruposViewSet] Actualizando grupo {kwargs.get('pk')}")
        print(f"[GruposViewSet] Datos recibidos: {request.data}")
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been used, we need to reload the instance
            # from the database to get the updated M2M fields.
            instance = self.get_object()
            
        # Serializar la instancia completa y actualizada para la respuesta
        response_serializer = self.get_serializer(instance)
        return Response(response_serializer.data)

    @action(detail=True, methods=['post'], url_path='generar-horario')
    def generar_horario(self, request, pk=None):
        """
        Endpoint para disparar la generación de horario para un único grupo.
        """
        grupo = self.get_object()
        periodo_activo = grupo.periodo

        if not periodo_activo:
            return Response(
                {"error": "El grupo no está asociado a un período académico válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"Iniciando generador de horarios para el grupo '{grupo.codigo_grupo}' en el período '{periodo_activo.nombre_periodo}'...")
        
        # Instanciar el servicio
        generator = ScheduleGeneratorService(periodo=periodo_activo)

        # Llamar al nuevo método específico para un grupo
        resultado = generator.generar_horario_para_grupo(grupo_id=grupo.grupo_id)

        if "error" in resultado:
            return Response(resultado, status=status.HTTP_404_NOT_FOUND)
        if "warning" in resultado:
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

        return Response(resultado, status=status.HTTP_200_OK)


class BloquesHorariosDefinicionViewSet(viewsets.ModelViewSet):
    queryset = BloquesHorariosDefinicion.objects.all()
    serializer_class = BloquesHorariosDefinicionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None # Deshabilitar paginación para este ViewSet


class DisponibilidadDocentesViewSet(viewsets.ModelViewSet):
    queryset = DisponibilidadDocentes.objects.select_related('docente', 'periodo', 'bloque_horario').all()
    serializer_class = DisponibilidadDocentesSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['docente', 'periodo']
    pagination_class = None # Deshabilitar paginación para este ViewSet


class HorariosAsignadosViewSet(viewsets.ModelViewSet):
    queryset = HorariosAsignados.objects.select_related(
        'grupo__carrera', 'docente', 'espacio', 'periodo', 'bloque_horario', 'materia'
    ).all()
    serializer_class = HorariosAsignadosSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'periodo': ['exact'],
        'grupo': ['exact', 'in'],
        'docente': ['exact', 'in'],
        'espacio': ['exact', 'in'],
        'dia_semana': ['exact'],
        'grupo__carrera': ['exact'],
    }
    pagination_class = None # Deshabilitar paginación para validaciones en el frontend
    throttle_scope = 'horarios_updates' # Rate limiting scope

    def perform_create(self, serializer):
        with transaction.atomic():
            instance = serializer.save()
            # Audit
            user = self.request.user if self.request.user.is_authenticated else None
            ScheduleAuditLog.objects.create(
                action='CREATE',
                model_name='HorariosAsignados',
                object_id=str(instance.pk),
                user=user,
                details=serializer.data
            )
            # Real-time Broadcast
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'schedule_updates',
                {
                    'type': 'schedule_update',
                    'message': 'New schedule created',
                    'type_of_change': 'CREATE',
                    'data': serializer.data
                }
            )

    def perform_update(self, serializer):
        # Optimistic Locking Check
        instance = serializer.instance
        client_updated_at = self.request.data.get('updated_at')
        
        if client_updated_at:
             # Convert DB timestamp to ISO string for comparison logic (or verify if DRF handles it)
             # Basic check: if timestamp differs significantly.
             # Ideally compare datetime objects. For now relying on client sending correct format.
             pass 

        # Note: In a real optimistic lock, we compare instance.updated_at with client_updated_at.
        # If mismatch -> raise Conflict. 
        # For this MVP, we will broadcast the update to avoid conflicts in frontend.
        
        with transaction.atomic():
            instance = serializer.save()
            # Audit
            user = self.request.user if self.request.user.is_authenticated else None
            ScheduleAuditLog.objects.create(
                action='UPDATE',
                model_name='HorariosAsignados',
                object_id=str(instance.pk),
                user=user,
                details=serializer.data
            )
            # Broadcast
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'schedule_updates',
                {
                    'type': 'schedule_update',
                    'message': 'Schedule updated',
                    'type_of_change': 'UPDATE',
                    'data': serializer.data
                }
            )

    def perform_destroy(self, instance):
        data_backup = HorariosAsignadosSerializer(instance).data
        with transaction.atomic():
            pk = instance.pk
            instance.delete()
            # Audit
            user = self.request.user if self.request.user.is_authenticated else None
            ScheduleAuditLog.objects.create(
                action='DELETE',
                model_name='HorariosAsignados',
                object_id=str(pk),
                user=user,
                details=data_backup
            )
            # Broadcast
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'schedule_updates',
                {
                    'type': 'schedule_update',
                    'message': 'Schedule deleted',
                    'type_of_change': 'DELETE',
                    'data': {'horario_id': pk}
                }
            )


class ConfiguracionRestriccionesViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionRestricciones.objects.select_related('periodo_aplicable').all()
    serializer_class = ConfiguracionRestriccionesSerializer
    permission_classes = [permissions.AllowAny]

class GeneracionHorarioView(viewsets.ViewSet):
    permission_classes = [AllowAny] # Reemplaza AllowAny con un permiso adecuado
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=False, methods=['post'], url_path='generar-horario-automatico')
    def generar_horario(self, request):
        periodo_id = request.data.get('periodo_id')
        if not periodo_id:
            logger.warning(f"Intento de generar horario sin periodo_id por usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}")
            return Response({"error": "Se requiere el ID del período académico."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = PeriodoAcademico.objects.get(pk=periodo_id)
        except PeriodoAcademico.DoesNotExist:
            logger.warning(f"Intento de generar horario para periodo_id no existente: {periodo_id} por usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}")
            return Response({"error": "Período académico no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        logger.info(f"Iniciando generación SÍNCRONA para periodo_id: {periodo_id} (Solicitado por: {request.user.username if request.user.is_authenticated else 'Anónimo'})")

        # Pasamos la instancia del logger de la vista al servicio
        generator_service = ScheduleGeneratorService(periodo=periodo, stdout_ref=logger)

        try:
            resultado = generator_service.generar_horarios_automaticos()
            logger.info(f"Generación SÍNCRONA para periodo_id: {periodo_id} completada. Stats: {resultado.get('stats')}")
            
            # Convertir conflictos no resueltos a formato serializable
            unresolved_conflicts_serializable = []
            for conflict in resultado.get('unresolved_conflicts', []):
                unresolved_conflicts_serializable.append({
                    'grupo_id': conflict.grupo.grupo_id,
                    'grupo_codigo': conflict.grupo.codigo_grupo,
                    'materia_id': conflict.materia.materia_id,
                    'materia_nombre': conflict.materia.nombre_materia,
                    'sesiones_necesarias': conflict.sesiones_necesarias,
                    'sesiones_programadas': conflict.sesiones_programadas,
                    'razon': f"No se pudo programar {conflict.sesiones_necesarias - conflict.sesiones_programadas} sesiones de {conflict.materia.nombre_materia}"
                })
            
            return Response({
                "message": f"Proceso de generación de horarios para {periodo.nombre_periodo} completado (síncrono).",
                "stats": resultado.get('stats', {}),
                "unresolved_conflicts": unresolved_conflicts_serializable
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error catastrófico en generación síncrona de horario para periodo_id {periodo_id}: {str(e)}", exc_info=True)
            return Response({"error": f"Ocurrió un error crítico durante la generación síncrona: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='exportar-horarios-excel')
    def exportar_horarios(self, request):
        periodo_id = request.query_params.get('periodo_id')
        if not periodo_id:
            logger.warning(f"Intento de exportar horarios sin periodo_id por usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}")
            return Response({"error": "Se requiere el parámetro 'periodo_id'."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"Solicitud de exportación a Excel para periodo_id: {periodo_id} por usuario: {request.user.username if request.user.is_authenticated else 'Anónimo'}")
        # ... (Aquí iría la lógica de exportación a Excel) ...
        return Response({"message": "Funcionalidad de exportación a Excel pendiente de implementación detallada."}, status=status.HTTP_501_NOT_IMPLEMENTED)

    @action(detail=False, methods=['post'], url_path='importar-disponibilidad-excel')
    def importar_disponibilidad_excel(self, request):
        """
        Importa la disponibilidad del docente desde un archivo Excel.
        Aplica la regla: si hay al menos un '1' en cualquier bloque de un turno y día, todos los bloques de ese turno y día se marcan como disponibles; si todos están vacíos o 0, todos se marcan como no disponibles.
        Registra el id del usuario que subió el archivo si está autenticado.
        """
        print("=== INICIO IMPORTAR DISPONIBILIDAD EXCEL ===")
        print("Request data:", request.data)
        print("Request FILES:", request.FILES)
        print("Request user:", request.user)
        
        file = request.FILES.get('file')
        periodo_id = request.data.get('periodo_id')
        docente_id = request.data.get('docente_id')
        usuario = request.user if request.user and request.user.is_authenticated else None
        
        print("File:", file)
        print("Periodo ID:", periodo_id)
        print("Docente ID:", docente_id)
        print("Usuario:", usuario)
        
        if not file or not periodo_id or not docente_id:
            print("ERROR: Faltan datos requeridos")
            print("File presente:", bool(file))
            print("Periodo ID presente:", bool(periodo_id))
            print("Docente ID presente:", bool(docente_id))
            return Response({'error': 'Faltan datos requeridos (archivo, periodo_id, docente_id).'}, status=status.HTTP_400_BAD_REQUEST)
        print("Archivo recibido:", file)
        print("Nombre:", getattr(file, 'name', None))
        print("Tamaño:", getattr(file, 'size', None))
        print("Tipo:", getattr(file, 'content_type', None))
        
        try:
            print("Intentando cargar workbook...")
            wb = openpyxl.load_workbook(file)
            print("Workbook cargado correctamente.")
            ws = wb.active
            print("Worksheet activo:", ws.title)
            rows = list(ws.iter_rows(values_only=True))
            print("Total de filas leídas:", len(rows))
            
            if not rows:
                print("ERROR: No hay filas en el archivo")
                return Response({'error': 'El archivo Excel está vacío.'}, status=status.HTTP_400_BAD_REQUEST)
            
            headers = [str(h).strip() for h in rows[0]]
            print("Encabezados detectados:", headers)
            
            # Validar que existan los encabezados requeridos
            if 'Bloque horario' not in headers:
                print("ERROR: No se encontró columna 'Bloque horario'")
                return Response({'error': 'El archivo debe tener una columna llamada "Bloque horario".'}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'Turno' not in headers:
                print("ERROR: No se encontró columna 'Turno'")
                return Response({'error': 'El archivo debe tener una columna llamada "Turno".'}, status=status.HTTP_400_BAD_REQUEST)
            
            idx_bloque = headers.index('Bloque horario')
            idx_turno = headers.index('Turno')
            dias_indices = [(i, headers[i]) for i in range(len(headers)) if headers[i] in ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado']]
            
            print("Índice bloque:", idx_bloque)
            print("Índice turno:", idx_turno)
            print("Días encontrados:", dias_indices)
            
        except Exception as e:
            print("Error al leer el archivo Excel:", str(e))
            import traceback
            print("Traceback completo:")
            traceback.print_exc()
            return Response({'error': f'Error leyendo el archivo Excel: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        # Construir estructura: {dia: {turno: [fila_index, ...]}}
        turnos = ['Mañana','Tarde','Noche']
        dias_map = {'Lunes':1,'Martes':2,'Miércoles':3,'Jueves':4,'Viernes':5,'Sábado':6}
        errores = []
        bloques_por_turno_dia = {dia:{} for dia in dias_map.values()}
        for row_idx, row in enumerate(rows[1:], start=1):
            # Validaciones y llenado de errores (como antes)
            if not row or len(row) < 2:  # Debe tener al menos 'Bloque horario' y 'Turno'
                errores.append(f'Fila {row_idx+1}: Fila vacía o faltan columnas.')
                continue
            if idx_bloque >= len(row) or idx_turno >= len(row):
                errores.append(f'Fila {row_idx+1}: Faltan columnas para Bloque horario o Turno.')
                continue
            bloque_hora = row[idx_bloque]
            turno = row[idx_turno]
            if not isinstance(bloque_hora, str) or not (len(bloque_hora) == 8 and bloque_hora.count(':') == 2):
                errores.append(f'Fila {row_idx+1}: Formato de bloque horario inválido. Debe ser HH:MM:SS')
            if turno not in ['Mañana','Tarde','Noche']:
                errores.append(f'Fila {row_idx+1}: Turno inválido. Solo se permite Mañana, Tarde o Noche.')
            for idx, dia_nombre in dias_indices:
                if idx >= len(row):
                    continue
                valor = row[idx]
                if valor not in (None, '', 1, '1', 0, '0'):
                    errores.append(f'Fila {row_idx+1}, columna {dia_nombre}: Solo se permite 1, 0 o vacío.')
        if errores:
            return Response({'errores': errores}, status=status.HTTP_400_BAD_REQUEST)
        # Solo construir bloques_por_turno_dia y procesar si no hay errores
        bloques_por_turno_dia = {dia:{} for dia in dias_map.values()}
        for row_idx, row in enumerate(rows[1:], start=1):
            if not row or len(row) < 2:
                continue
            if idx_bloque >= len(row) or idx_turno >= len(row):
                continue
            bloque_hora = row[idx_bloque]
            turno = row[idx_turno]
            for idx, dia_nombre in dias_indices:
                if idx >= len(row):
                    continue
                dia = dias_map[dia_nombre]
                if turno not in bloques_por_turno_dia[dia]:
                    bloques_por_turno_dia[dia][turno] = []
                bloques_por_turno_dia[dia][turno].append((row_idx, idx, bloque_hora))
        # Determinar disponibilidad por turno y día
        disponibilidad_final = []
        for dia, turnos_dict in bloques_por_turno_dia.items():
            for turno, celdas in turnos_dict.items():
                # Si hay al menos un 1, todos disponibles; si todos vacíos/0, todos no disponibles
                hay_disponible = any(str(rows[row_idx][col_idx]).strip() == '1' for row_idx, col_idx, _ in celdas)
                for row_idx, col_idx, bloque_hora in celdas:
                    disponibilidad_final.append({
                        'dia': dia,
                        'turno': turno,
                        'bloque_hora': bloque_hora,
                        'disponible': hay_disponible
                    })
        # Mapear bloque_hora, turno y día a bloque_horario_id
        from .models import BloquesHorariosDefinicion
        bloques_db = BloquesHorariosDefinicion.objects.all()
        bloque_map = {}
        for b in bloques_db:
            clave = (str(b.hora_inicio), b.turno, b.dia_semana)
            bloque_map[clave] = b.bloque_def_id
        # Registrar en la base de datos
        from .models import DisponibilidadDocentes
        with transaction.atomic():
            for disp in disponibilidad_final:
                clave_bloque = (
                    str(disp['bloque_hora']),
                    'M' if disp['turno']=='Mañana' else 'T' if disp['turno']=='Tarde' else 'N',
                    disp['dia']
                )
                bloque_id = bloque_map.get(clave_bloque)
                if not bloque_id:
                    continue
                obj, created = DisponibilidadDocentes.objects.update_or_create(
                    docente_id=docente_id,
                    periodo_id=periodo_id,
                    dia_semana=disp['dia'],
                    bloque_horario_id=bloque_id,
                    defaults={
                        'esta_disponible': disp['disponible'],
                        'origen_carga': 'EXCEL'
                    }
                )
        print("=== FINALIZADO IMPORTAR DISPONIBILIDAD EXCEL ===")
        print(f"Registros procesados: {len(disponibilidad_final)}")
        return Response({'message': f'Se importaron {len(disponibilidad_final)} registros de disponibilidad.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_metrics(request, periodo_id=None):
    """Obtener métricas del sistema"""
    try:
        if periodo_id:
            metrics = MetricsManager.get_metrics(periodo_id)
        else:
            metrics = MetricsManager.get_metrics()
        
        return Response({
            'status': 'success',
            'data': metrics
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_audit_logs(request, periodo_id=None):
    """Obtener logs de auditoría"""
    try:
        limit = int(request.GET.get('limit', 50))
        
        if periodo_id:
            audit_logs = AuditManager.get_audit_logs(periodo_id, limit)
        else:
            audit_logs = AuditManager.get_audit_logs(None, limit)
        
        return Response({
            'status': 'success',
            'data': audit_logs
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_audit_summary(request, periodo_id=None):
    """Obtener resumen de auditoría"""
    try:
        if periodo_id:
            summary = AuditManager.get_audit_summary(periodo_id)
        else:
            summary = AuditManager.get_audit_summary()
        
        return Response({
            'status': 'success',
            'data': summary
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_health(request):
    """Obtener estado de salud del sistema"""
    try:
        # Métricas globales
        global_metrics = MetricsManager.get_metrics()
        
        # Resumen de auditoría global
        audit_summary = AuditManager.get_audit_summary()
        
        # Estado de salud
        health_status = {
            'status': 'healthy',
            'timestamp': 'now',
            'metrics': global_metrics,
            'audit_summary': audit_summary
        }
        
        return Response({
            'status': 'success',
            'data': health_status
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
