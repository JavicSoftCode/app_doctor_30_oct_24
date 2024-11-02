# Generated by Django 5.1.2 on 2024-11-02 01:44

import doctor.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_empleado_sueldo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicamento',
            name='cantidad',
            field=models.PositiveIntegerField(validators=[doctor.utils.validate_cantidad], verbose_name='Stock'),
        ),
        migrations.AlterField(
            model_name='medicamento',
            name='precio',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[doctor.utils.validate_precio], verbose_name='Precio'),
        ),
    ]
