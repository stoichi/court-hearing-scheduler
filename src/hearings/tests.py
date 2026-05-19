from datetime import timedelta, time

from model_bakery import baker
from rest_framework.test import APITestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Role, User
from .models import CourtHearing


class CourtHearingAPITestCase(APITestCase):
    def setUp(self) -> None:
        """
        Build dummy roles, users, and a single hearing used by the API tests.
        """
        # Pre-make roles
        self.judge_role = baker.make(Role, name="Judge")
        self.prosecutor_role = baker.make(Role, name="Prosecutor")
        self.defense_lawyer_role = baker.make(Role, name="Defense Lawyer")

        # Pre-make users
        self.judge = baker.make(User, role=self.judge_role)
        self.prosecutor = baker.make(User, role=self.prosecutor_role)
        self.defense_lawyer = baker.make(User, role=self.defense_lawyer_role)

        # Create a hearing to test against
        self.hearing_date = timezone.localdate() + timedelta(days=30)
        self.other_date = self.hearing_date + timedelta(days=21)
        self.hearing = baker.make(
            CourtHearing,
            name="Test Hearing",
            date=self.hearing_date,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

    def test_list_hearings(self) -> None:
        """
        Verify the list endpoint returns all hearings with their core fields.
        """
        response = self.client.get(reverse("hearings:hearing-api-list"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.hearing.pk)
        self.assertEqual(data[0]["name"], "Test Hearing")
        self.assertEqual(data[0]["date"], self.hearing_date.isoformat())
        self.assertEqual(data[0]["start_time"], "09:00:00")
        self.assertEqual(data[0]["end_time"], "10:00:00")

    def test_create_hearing(self) -> None:
        """
        Verify a valid payload creates a new hearing and returns its serialized form.
        """
        payload = {
            "name": "New Hearing",
            "date": self.other_date.isoformat(),
            "start_time": "11:00:00",
            "end_time": "12:00:00",
            "participants": [self.judge.id],
        }
        response = self.client.post(
            reverse("hearings:hearing-api-list"),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "New Hearing")
        self.assertEqual(data["date"], self.other_date.isoformat())
        self.assertEqual(data["start_time"], "11:00:00")
        self.assertEqual(data["end_time"], "12:00:00")
        self.assertTrue(CourtHearing.objects.filter(name="New Hearing").exists())

    def test_create_hearing_conflict(self) -> None:
        """
        Verify creating a hearing that overlaps an existing one is rejected.
        """
        payload = {
            "name": "Conflicting Hearing",
            "date": self.hearing_date.isoformat(),
            "start_time": "09:30:00",
            "end_time": "10:30:00",
            "participants": [self.judge.id],
        }
        response = self.client.post(
            reverse("hearings:hearing-api-list"),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.json())
        self.assertEqual(CourtHearing.objects.count(), 1)

    def test_retrieve_hearing(self) -> None:
        """
        Verify the detail endpoint returns the serialized hearing by primary key.
        """
        response = self.client.get(reverse("hearings:hearing-api-detail", kwargs={"pk": self.hearing.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.hearing.pk)
        self.assertEqual(data["name"], "Test Hearing")
        self.assertEqual(data["date"], self.hearing_date.isoformat())
        self.assertEqual(data["start_time"], "09:00:00")
        self.assertEqual(data["end_time"], "10:00:00")

    def test_update_hearing(self) -> None:
        """
        Verify a patch request updates the hearing fields and persists the changes.
        """
        payload = {
            "name": "Updated Hearing",
            "start_time": "09:30:00",
            "end_time": "10:30:00",
        }
        response = self.client.patch(
            reverse("hearings:hearing-api-detail", kwargs={"pk": self.hearing.pk}),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated Hearing")
        self.assertEqual(data["start_time"], "09:30:00")
        self.assertEqual(data["end_time"], "10:30:00")
        self.hearing.refresh_from_db()
        self.assertEqual(self.hearing.name, "Updated Hearing")
        self.assertEqual(self.hearing.start_time, time(9, 30))
        self.assertEqual(self.hearing.end_time, time(10, 30))

    def test_delete_hearing(self) -> None:
        """
        Verify a delete request removes the hearing from the database.
        """
        response = self.client.delete(reverse("hearings:hearing-api-detail", kwargs={"pk": self.hearing.pk}))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(CourtHearing.objects.filter(pk=self.hearing.pk).exists())

    def test_get_participants(self) -> None:
        """
        Verify the participants endpoint returns the users attached to the hearing.
        """
        self.hearing.participants.add(self.judge)
        response = self.client.get(reverse("hearings:hearing-api-participants", kwargs={"pk": self.hearing.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.judge.id)
        self.assertEqual(data[0]["username"], self.judge.username)

    def test_add_participants(self) -> None:
        """
        Verify posting user ids attaches them as participants to the hearing.
        """
        payload = {"user_ids": [self.judge.id, self.prosecutor.id]}
        response = self.client.post(
            reverse("hearings:hearing-api-participants", kwargs={"pk": self.hearing.pk}),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        participant_ids = [u["id"] for u in data]
        self.assertIn(self.judge.id, participant_ids)
        self.assertIn(self.prosecutor.id, participant_ids)
        self.assertCountEqual(
            list(self.hearing.participants.values_list("id", flat=True)),
            [self.judge.id, self.prosecutor.id],
        )

    def test_remove_participants(self) -> None:
        """
        Verify deleting user ids detaches only the specified participants from the hearing.
        """
        self.hearing.participants.add(self.judge, self.prosecutor)
        payload = {"user_ids": [self.judge.id]}
        response = self.client.delete(
            reverse("hearings:hearing-api-participants", kwargs={"pk": self.hearing.pk}),
            data=payload,
            format="json",
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(self.hearing.participants.filter(id=self.judge.id).exists())
        self.assertTrue(self.hearing.participants.filter(id=self.prosecutor.id).exists())


class HearingHTMLViewTestCase(APITestCase):
    def setUp(self) -> None:
        """
        Build a baseline role, user, and hearing used by the HTML view tests.
        """
        self.judge_role = baker.make(Role, name="Judge")
        self.judge = baker.make(User, role=self.judge_role)
        self.hearing_date = timezone.localdate() + timedelta(days=60)
        self.create_date = self.hearing_date + timedelta(days=17)
        self.htmx_create_date = self.hearing_date + timedelta(days=18)
        self.hearing = baker.make(
            CourtHearing,
            name="Test Hearing",
            date=self.hearing_date,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

    def test_list_view(self) -> None:
        """
        Verify the list page renders successfully and includes existing hearings.
        """
        response = self.client.get(reverse("hearings:hearing-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Hearing")

    def test_list_view_htmx(self) -> None:
        """
        Verify the list view responds to HTMX requests with the hearing rows partial.
        """
        response = self.client.get(
            reverse("hearings:hearing-list"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Hearing")

    def test_create_view_get(self) -> None:
        """
        Verify the create form page loads successfully.
        """
        response = self.client.get(reverse("hearings:hearing-create"))
        self.assertEqual(response.status_code, 200)

    def test_create_view_post(self) -> None:
        """
        Verify submitting the create form persists the hearing and redirects to the list.
        """
        data = {
            "name": "New Hearing",
            "description": "Test hearing",
            "date": self.create_date.isoformat(),
            "start_time": "09:00",
            "end_time": "10:00",
            "participants": [self.judge.id],
        }
        response = self.client.post(reverse("hearings:hearing-create"), data=data)
        self.assertRedirects(response, reverse("hearings:hearing-list"), fetch_redirect_response=False)
        hearing = CourtHearing.objects.get(name="New Hearing")
        self.assertEqual(hearing.date, self.create_date)
        self.assertEqual(hearing.start_time, time(9, 0))
        self.assertEqual(hearing.end_time, time(10, 0))
        self.assertIn(self.judge, hearing.participants.all())

    def test_create_view_htmx_post(self) -> None:
        """
        Verify an HTMX create request saves the hearing and returns the refresh trigger response.
        """
        data = {
            "name": "HTMX Hearing",
            "description": "",
            "date": self.htmx_create_date.isoformat(),
            "start_time": "11:00",
            "end_time": "12:00",
            "participants": [self.judge.id],
        }
        response = self.client.post(
            reverse("hearings:hearing-create"),
            data=data,
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers.get("HX-Trigger"), "refresh-hearings")
        hearing = CourtHearing.objects.get(name="HTMX Hearing")
        self.assertEqual(hearing.date, self.htmx_create_date)
        self.assertEqual(hearing.start_time, time(11, 0))
        self.assertEqual(hearing.end_time, time(12, 0))

    def test_update_view_get(self) -> None:
        """
        Verify the update form page loads and is pre-populated with the hearing's data.
        """
        response = self.client.get(reverse("hearings:hearing-update", kwargs={"pk": self.hearing.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Hearing")

    def test_update_view_post(self) -> None:
        """
        Verify submitting the update form persists the changes and redirects to the list.
        """
        data = {
            "name": "Updated Hearing",
            "description": "",
            "date": self.hearing_date.isoformat(),
            "start_time": "09:00",
            "end_time": "10:00",
            "participants": [self.judge.id],
        }
        response = self.client.post(
            reverse("hearings:hearing-update", kwargs={"pk": self.hearing.pk}),
            data=data,
        )
        self.assertRedirects(response, reverse("hearings:hearing-list"), fetch_redirect_response=False)
        self.hearing.refresh_from_db()
        self.assertEqual(self.hearing.name, "Updated Hearing")
        self.assertEqual(self.hearing.date, self.hearing_date)
        self.assertEqual(self.hearing.start_time, time(9, 0))
        self.assertEqual(self.hearing.end_time, time(10, 0))

    def test_update_view_htmx_post(self) -> None:
        """
        Verify an HTMX update request saves the changes and returns the refresh trigger response.
        """
        data = {
            "name": "HTMX Updated",
            "description": "",
            "date": self.hearing_date.isoformat(),
            "start_time": "09:00",
            "end_time": "10:00",
            "participants": [self.judge.id],
        }
        response = self.client.post(
            reverse("hearings:hearing-update", kwargs={"pk": self.hearing.pk}),
            data=data,
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers.get("HX-Trigger"), "refresh-hearings")
        self.hearing.refresh_from_db()
        self.assertEqual(self.hearing.name, "HTMX Updated")
        self.assertEqual(self.hearing.date, self.hearing_date)
        self.assertEqual(self.hearing.start_time, time(9, 0))
        self.assertEqual(self.hearing.end_time, time(10, 0))

    def test_delete_view_get(self) -> None:
        """
        Verify the delete confirmation page loads and references the hearing being removed.
        """
        response = self.client.get(reverse("hearings:hearing-delete", kwargs={"pk": self.hearing.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Hearing")

    def test_delete_view_post(self) -> None:
        """
        Verify submitting the delete form removes the hearing and redirects to the list.
        """
        response = self.client.post(reverse("hearings:hearing-delete", kwargs={"pk": self.hearing.pk}))
        self.assertRedirects(response, reverse("hearings:hearing-list"), fetch_redirect_response=False)
        self.assertFalse(CourtHearing.objects.filter(pk=self.hearing.pk).exists())

    def test_delete_view_htmx_post(self) -> None:
        """
        Verify an HTMX delete request removes the hearing and returns the refresh trigger response.
        """
        response = self.client.post(
            reverse("hearings:hearing-delete", kwargs={"pk": self.hearing.pk}),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers.get("HX-Trigger"), "refresh-hearings")
        self.assertFalse(CourtHearing.objects.filter(pk=self.hearing.pk).exists())
