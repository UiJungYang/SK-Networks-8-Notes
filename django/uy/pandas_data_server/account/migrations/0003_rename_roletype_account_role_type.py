# Generated by Django 5.1.5 on 2025-02-05 06:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0002_rename_roletype_accountroletype_role_type"),
    ]

    operations = [
        migrations.RenameField(
            model_name="account",
            old_name="roleType",
            new_name="role_type",
        ),
    ]
