import django
from django.conf import settings
import os
from dotenv import load_dotenv

load_dotenv()


def init_django():
    if settings.configured:
        return

    settings.configure(
        INSTALLED_APPS=[
            "db",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.getenv("DB_NAME"),
                "USER": os.getenv("DB_USER"),
                "PASSWORD": os.getenv("DB_PASSWORD"),
                "HOST": os.getenv("DB_HOST"),
                "PORT": os.getenv("DB_PORT"),
            }
        },
    )
    django.setup()
