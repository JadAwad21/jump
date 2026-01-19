from rest_framework import permissions

class IsInvestigator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               hasattr(request.user, 'role_bindings') and \
               request.user.role_bindings.filter(role__name__in=['Investigator', 'SystemAdmin']).exists()

class IsAuditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               hasattr(request.user, 'role_bindings') and \
               request.user.role_bindings.filter(role__name__in=['Auditor', 'SystemAdmin']).exists()

class IsCourt(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               hasattr(request.user, 'role_bindings') and \
               request.user.role_bindings.filter(role__name__in=['Court', 'SystemAdmin']).exists()

class CanResolveAnonymous(permissions.BasePermission):
    """Court and Admin can resolve anonymous GUID to investigator name"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               hasattr(request.user, 'role_bindings') and \
               request.user.role_bindings.filter(role__name__in=['Court', 'SystemAdmin']).exists()
