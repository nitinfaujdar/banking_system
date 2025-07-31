from rest_framework.permissions import BasePermission

class IsInGroup(BasePermission):
    """
    Allows access only to users in a specific group.
    """

    def has_permission(self, request, view):
        required_groups = getattr(view, 'required_groups', [])
        if not required_groups:
            return True  # No specific group required
        return request.user.is_authenticated and request.user.groups.filter(name__in=required_groups).exists()
