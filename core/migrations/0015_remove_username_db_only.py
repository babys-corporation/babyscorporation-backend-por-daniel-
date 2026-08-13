from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_usuario_managers_remove_usuario_username'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE core_usuario DROP COLUMN IF EXISTS username;',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
