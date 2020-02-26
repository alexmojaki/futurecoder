from django.core.management.base import BaseCommand

from main.models import User


class Command(BaseCommand):
    help = "Initialises the database with essentials, particularly an admin user account"

    def handle(self, *args, **kwargs):
        if User.objects.exists():
            return

        print("Creating superuser")
        User.objects.create_superuser(
            username="admin",
            password="admin",
            first_name="Admin",
            last_name="Adminson",
            email="admin@example.com",
        )
