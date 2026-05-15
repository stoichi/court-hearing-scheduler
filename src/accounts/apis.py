from rest_framework.viewsets import ModelViewSet

from .models import Role, User
from .serializers import RoleSerializer, UserSerializer


class RoleViewSet(ModelViewSet):
    """CRUD API endpoints for Role records."""

    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(ModelViewSet):
    """CRUD API endpoints for User records."""

    queryset = User.objects.all().select_related("role")
    serializer_class = UserSerializer
