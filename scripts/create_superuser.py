import os

from django.contrib.auth import get_user_model

User = get_user_model()

email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

if not email or not password:
    print("Variáveis de superusuário não configuradas; pulando criação.")
else:
    user = User.objects.filter(email=email).first()

    if user:
        changed = False

        if not user.is_staff:
            user.is_staff = True
            changed = True

        if not user.is_superuser:
            user.is_superuser = True
            changed = True

        if not user.is_active:
            user.is_active = True
            changed = True

        if changed:
            user.set_password(password)
            user.save()
            print(f"Superusuário atualizado: {email}")
        else:
            print(f"Superusuário já existe: {email}")
    else:
        user = User.objects.create_superuser(
            email=email,
            password=password,
        )
        print(f"Superusuário criado: {email}")