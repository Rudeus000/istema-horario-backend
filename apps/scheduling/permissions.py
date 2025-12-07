# apps/scheduling/permissions.py
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado: Solo admins pueden modificar,
    todos los usuarios autenticados pueden leer.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class IsAdminOrCoordinator(permissions.BasePermission):
    """
    Solo administradores o coordinadores pueden acceder.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar si es admin o coordinador
        user_groups = request.user.groups.values_list('name', flat=True)
        return request.user.is_staff or 'Coordinador' in user_groups


class CanGenerateSchedules(permissions.BasePermission):
    """
    Permiso para generar horarios automáticos.
    Solo administradores o coordinadores académicos pueden generar horarios.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['Administrador', 'Coordinador Académico', 'Admins']
        return request.user.is_staff or any(g in allowed_groups for g in user_groups)


class CanManageRestrictions(permissions.BasePermission):
    """
    Permiso para gestionar restricciones del sistema.
    Solo administradores pueden modificar restricciones.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True  # Todos pueden leer restricciones
        
        return request.user.is_staff  # Solo admins pueden modificar

