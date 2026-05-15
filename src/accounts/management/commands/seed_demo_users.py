from django.core.management.base import BaseCommand

from accounts.models import Role, User


ROLES = [
    "Judge",
    "Prosecution Lawyer",
    "Defense Lawyer",
    "Witness",
    "Public Observer",
]

# (username, first_name, last_name, role_name)
DEMO_USERS = [
    ("mhollister", "Margaret", "Hollister",  "Judge"),
    ("dokafor",    "Daniel",   "Okafor",     "Judge"),
    ("ytanaka",    "Yuki",     "Tanaka",     "Judge"),

    ("ewhitfield", "Eleanor",  "Whitfield",  "Prosecution Lawyer"),
    ("cramirez",   "Carlos",   "Ramirez",    "Prosecution Lawyer"),
    ("psingh",     "Priya",    "Singh",      "Prosecution Lawyer"),

    ("tbennett",   "Thomas",   "Bennett",    "Defense Lawyer"),
    ("lnguyen",    "Linh",     "Nguyen",     "Defense Lawyer"),
    ("aosullivan", "Aoife",    "O'Sullivan", "Defense Lawyer"),

    ("jcarter",    "James",    "Carter",     "Witness"),
    ("apetrov",    "Anna",     "Petrov",     "Witness"),
    ("rmccoy",     "Rebecca",  "McCoy",      "Witness"),
    ("oahmed",     "Omar",     "Ahmed",      "Witness"),

    ("hbrown",     "Henry",    "Brown",      "Public Observer"),
    ("gfischer",   "Greta",    "Fischer",    "Public Observer"),
    ("hkimura",    "Haruto",   "Kimura",     "Public Observer"),
]

#####################################################################################
# Only for demo purposes, never store real user data or passwords in the repository
PASSWORD = "demo1234"
ADMIN_PASSWORD = "admin"
#####################################################################################


class Command(BaseCommand):
    help = "Seed demo roles and users."

    def handle(self, *args, **options) -> None:
        """
        Seed the database with the demo roles, an admin superuser, and demo users for each role.
        """
        # Roles
        for name in ROLES:
            _, created = Role.objects.get_or_create(name=name)
            self.stdout.write(f"{'Created' if created else 'Exists '} role: {name}")

        # Admin
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@court.com",
                "first_name": "Court",
                "last_name": "Administrator",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        if created:
            admin.set_password(ADMIN_PASSWORD)
            admin.save()
        self.stdout.write(f"{'Created' if created else 'Exists '} superuser: admin")

        # Users
        for username, first, last, role_name in DEMO_USERS:
            role = Role.objects.get(name__iexact=role_name)
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": f"{username}@court.com",
                    "role": role,
                    "is_active": True,
                },
            )
            if created:
                user.set_password(PASSWORD)
                user.save()
            self.stdout.write(
                f"{'Created' if created else 'Exists '} user: {username} ({role_name})"
            )

        self.stdout.write(self.style.SUCCESS("Done."))