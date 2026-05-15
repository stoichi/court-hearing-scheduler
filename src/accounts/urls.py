from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import apis

app_name = "accounts"

router = DefaultRouter()
router.register(r"roles", apis.RoleViewSet, basename="role-api")
router.register(r"users", apis.UserViewSet, basename="user-api")

urlpatterns = [
    path("api/", include(router.urls)),
]
