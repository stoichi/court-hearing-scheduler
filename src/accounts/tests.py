from model_bakery import baker
from rest_framework.test import APITestCase
from django.urls import reverse

from .models import Role, User


class RoleAPITestCase(APITestCase):
    def setUp(self) -> None:
        """
        Build a baseline role used by the role API tests.
        """
        self.role = baker.make(Role, name="Judge")

    def test_list_roles(self) -> None:
        """
        Verify the list endpoint returns all roles with their id and name.
        """
        response = self.client.get(reverse("accounts:role-api-list"))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.role.id)
        self.assertEqual(data[0]["name"], "Judge")

    def test_create_role(self) -> None:
        """
        Verify a valid payload creates a new role.
        """
        payload = {"name": "Witness"}
        response = self.client.post(
            reverse("accounts:role-api-list"),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Role.objects.filter(name="Witness").exists())

    def test_create_role_duplicate(self) -> None:
        """
        Verify creating a role with an existing name is rejected.
        """
        payload = {"name": "Judge"}
        response = self.client.post(
            reverse("accounts:role-api-list"),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_retrieve_role(self) -> None:
        """
        Verify the detail endpoint returns the role by primary key.
        """
        response = self.client.get(reverse("accounts:role-api-detail", kwargs={"pk": self.role.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Judge")

    def test_update_role(self) -> None:
        """
        Verify a patch request updates the role's name and persists the change.
        """
        payload = {"name": "Chief Judge"}
        response = self.client.patch(
            reverse("accounts:role-api-detail", kwargs={"pk": self.role.pk}),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.role.refresh_from_db()
        self.assertEqual(self.role.name, "Chief Judge")

    def test_delete_role(self) -> None:
        """
        Verify a delete request removes the role from the database.
        """
        response = self.client.delete(reverse("accounts:role-api-detail", kwargs={"pk": self.role.pk}))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Role.objects.filter(pk=self.role.pk).exists())


class UserAPITestCase(APITestCase):
    def setUp(self) -> None:
        """
        Build baseline roles and a user used by the user API tests.
        """
        self.role = baker.make(Role, name="Prosecutor")
        self.other_role = baker.make(Role, name="Defense Lawyer")
        self.user = baker.make(User, role=self.role, username="testuser")

    def test_list_users(self) -> None:
        """
        Verify the list endpoint returns users with their nested role data.
        """
        response = self.client.get(reverse("accounts:user-api-list"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(
            {
                "id": self.user.id,
                "username": self.user.username,
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "role": {
                    "id": self.role.id,
                    "name": self.role.name,
                },
            },
            data,
        )

    def test_create_user_with_role(self) -> None:
        """
        Verify creating a user with a role_id assigns the nested role on the response.
        """
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "role_id": self.role.pk,
        }
        response = self.client.post(
            reverse("accounts:user-api-list"),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data["username"], payload["username"])
        self.assertEqual(data["email"], payload["email"])
        self.assertEqual(data["first_name"], "")
        self.assertEqual(data["last_name"], "")
        self.assertEqual(data["role"]["id"], self.role.pk)
        self.assertEqual(data["role"]["name"], self.role.name)

    def test_create_user_without_role(self) -> None:
        """
        Verify creating a user without a role_id succeeds and leaves the role null.
        """
        payload = {
            "username": "noroleuser",
            "email": "norole@example.com",
        }
        response = self.client.post(
            reverse("accounts:user-api-list"),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(data["username"], payload["username"])
        self.assertEqual(data["email"], payload["email"])
        self.assertEqual(data["first_name"], "")
        self.assertEqual(data["last_name"], "")
        self.assertIsNone(data["role"])

    def test_retrieve_user(self) -> None:
        """
        Verify the detail endpoint returns the user with nested role data.
        """
        response = self.client.get(reverse("accounts:user-api-detail", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["id"], self.user.pk)
        self.assertEqual(data["username"], self.user.username)
        self.assertEqual(data["email"], self.user.email)
        self.assertEqual(data["first_name"], self.user.first_name)
        self.assertEqual(data["last_name"], self.user.last_name)
        self.assertEqual(data["role"]["id"], self.role.pk)
        self.assertEqual(data["role"]["name"], self.role.name)

    def test_update_user_role(self) -> None:
        """
        Verify a patch request reassigns the user's role and persists the change.
        """
        payload = {"role_id": self.other_role.pk}
        response = self.client.patch(
            reverse("accounts:user-api-detail", kwargs={"pk": self.user.pk}),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role.id, self.other_role.pk)

    def test_delete_user(self) -> None:
        """
        Verify a delete request removes the user from the database.
        """
        response = self.client.delete(reverse("accounts:user-api-detail", kwargs={"pk": self.user.pk}))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
