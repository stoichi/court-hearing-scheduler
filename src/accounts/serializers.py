from rest_framework import serializers

from .models import Role, User


class RoleSerializer(serializers.ModelSerializer):
    """Serializes Role records for the API."""

    class Meta:
        model = Role
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    """Serializes User records, embedding nested role data and accepting role_id on write."""

    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source="role",
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "role_id"]
