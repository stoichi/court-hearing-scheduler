from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    """A named role assignable to users."""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        """
        Build the human-readable label for the role.

        Return:
        - The role's name
        """
        return self.name


class User(AbstractUser):
    """Court hearing Participants and system users."""

    id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, blank=True)


    # Enforce email during superuser command
    REQUIRED_FIELDS = ['email']

    def __str__(self) -> str:
        """
        Build the human-readable label for the user.

        Return:
        - String combining the user's role and full name
        """
        return f"{self.role} | {self.first_name} {self.last_name}"
    