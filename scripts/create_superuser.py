import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if not email or not password:
    print("Variáveis de superusuário não configuradas.")
else:
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        },
    )

    if created:
        user.set_password(password)
        user.save()
        print(f"Superusuário criado: {email}")
    else:
        print(f"Superusuário já existe: {email}")