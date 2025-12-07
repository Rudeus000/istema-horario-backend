# apps/scheduling/exceptions.py
from rest_framework.exceptions import APIException
from rest_framework import status


class ScheduleGenerationError(APIException):
    """Error al generar horarios automáticamente"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Error al generar horarios'
    default_code = 'schedule_generation_error'


class PeriodoNotFoundError(APIException):
    """Período académico no encontrado"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Período académico no encontrado'
    default_code = 'periodo_not_found'


class InvalidExcelFormatError(APIException):
    """Formato de archivo Excel inválido"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Formato de archivo Excel inválido'
    default_code = 'invalid_excel_format'


class ConflictError(APIException):
    """Conflicto detectado en la asignación"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Conflicto detectado en la asignación'
    default_code = 'conflict_error'


class GrupoNotFoundError(APIException):
    """Grupo no encontrado"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Grupo no encontrado'
    default_code = 'grupo_not_found'


class DocenteNotFoundError(APIException):
    """Docente no encontrado"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Docente no encontrado'
    default_code = 'docente_not_found'

