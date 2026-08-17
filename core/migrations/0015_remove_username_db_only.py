from django.db import migrations


def drop_username_column(apps, schema_editor):
    if schema_editor.connection.vendor != 'sqlite':
        schema_editor.execute(
            'ALTER TABLE core_usuario DROP COLUMN IF EXISTS username;'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_usuario_managers_remove_usuario_username'),
    ]

    operations = [
        migrations.RunPython(drop_username_column, migrations.RunPython.noop),
    ]
