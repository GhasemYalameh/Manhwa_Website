from rest_framework import permissions
class IsOwnerOrAdmin(permissions.BasePermission):
    """
    a permission class to check a user is an owner of an object or is an admin.
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user and (request.user.is_staff or request.user == obj.user))
