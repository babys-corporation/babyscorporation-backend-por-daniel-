web: gunicorn app.wsgi --log-file -
release: python manage.py migrate --noinput && python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); u=U.objects.get(email='companheiro@gmail.com'); u.set_password('38208888E'); u.is_superuser=True; u.is_staff=True; u.is_active=True; u.save(); print('ADMIN:', u.email, 'STAFF:', u.is_staff, 'SUPER:', u.is_superuser, 'ACTIVE:', u.is_active, 'PASSWORD_OK:', u.check_password('38208888E'))"



#web: gunicorn app.wsgi --log-file -
#release: python manage.py migrate --noinput && python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); U.objects.filter(email='SEU_EMAIL').exists() or U.objects.create_superuser(email='companheiro@gmail.com', password='38208888E')"