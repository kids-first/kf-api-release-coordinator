from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser


class AdminPermission(permissions.BasePermission):
    message = 'Must be an admin'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(request.user, AnonymousUser):
            return False

        if 'ADMIN' in roles:
            return True


class DevPermission(permissions.BasePermission):
    """
    Only allow developers to modify and create this resource.
    Everyone may read
    """
    message = 'Must be a developer'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'POST' and request.path.endswith('health_checks'):
            return True

        if isinstance(request.user, AnonymousUser):
            return False

        roles = request.user.auth_roles

        if "ADMIN" in roles or "DEV" in roles:
            return True


class AdminOrReadOnlyPermission(permissions.BasePermission):
    """
    Only allow admin, or read only to everyone else.
    """

    message = "Must be an admin"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow anyone to trigger status checks, should be removed in favor
        # of an internal scheduler and made an admin-only action
        if view.action == "status_checks":
            return True

        if isinstance(request.user, AnonymousUser):
            return False

        roles = request.user.auth_roles

        if "ADMIN" in roles:
            return True


class GroupPermission(permissions.BasePermission):
    """
    The user must be in a group for the given object or it's related release's
    studies to be allowed to make modifications.
    Everone may read
    Eg:
      User is in Groups [SD_00000000, SD_00000001], they may modify this
      resource if it is related to SD_00000000 or SD_00000001, but not
      if its related to SD_AAAAAAAA
    """
    message = 'Not allowed'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow anyone to trigger status checks, should be removed in favor
        # of an internal scheduler and made an admin-only action
        if view.action == "status_checks":
            return True

        if isinstance(request.user, AnonymousUser):
            return False

        roles = request.user.auth_roles
        groups = request.user.auth_groups

        if 'ADMIN' in roles:
            return True

        # If the user is trying to create a release
        if request.method == 'POST' and 'studies' in request.data:
            # Check that the user is in groups for all studies in the release
            if hasattr(request.data, 'getlist'):
                return all([s in groups
                            for s in request.data.getlist('studies')])
            else:
                return all([s in groups
                            for s in request.data['studies']])
        # If the user is trying to publish a release
        if request.method == 'POST' and request.path.endswith('publish'):
            # Continue on to check object permissions
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(request.user, AnonymousUser):
            return False

        roles = request.user.auth_roles
        groups = request.user.auth_groups

        if 'ADMIN' in roles:
            return True

        if hasattr(obj, 'studies'):
            return all([s in groups for s in obj.studies])

        # If trying to access own release
        if hasattr(obj, 'author'):
            return obj.author == request.user.get('name', None)
