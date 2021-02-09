from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from main.models import User
from main.simple_settings import GOOGLE_APP


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
            developer_mode=True,
        )

        print("Modifying site")
        site = Site.objects.get()
        site.domain = "localhost:3000"
        site.name = "futurecoder"
        site.save()

        print("Adding Google app")
        google_app = SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id=GOOGLE_APP.ID,
            secret=GOOGLE_APP.SECRET,
            key="",
        )
        google_app.sites.add(site)
        google_app.save()
