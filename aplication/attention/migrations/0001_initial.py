# Generated by Django 5.1.2 on 2024-11-02 19:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HorarioAtencion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.CharField(choices=[('lunes', 'Lunes'), ('martes', 'Martes'), ('miercoles', 'Miércoles'), ('jueves', 'Jueves'), ('viernes', 'Viernes'), ('sábado', 'Sábado'), ('domingo', 'Domingo')], max_length=10, unique=True, verbose_name='Día de la Semana')),
                ('hora_inicio', models.TimeField(verbose_name='Hora de Inicio')),
                ('hora_fin', models.TimeField(verbose_name='Hora de Fin')),
                ('Intervalo_desde', models.TimeField(verbose_name='Intervalo desde')),
                ('Intervalo_hasta', models.TimeField(verbose_name='Intervalo Hasta')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name': 'Horario de Atenciónl Doctor',
                'verbose_name_plural': 'Horarios de Atención de los Doctores',
            },
        ),
        migrations.CreateModel(
            name='ServiciosAdicionales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_servicio', models.CharField(max_length=255, verbose_name='Nombre del Servicio')),
                ('costo_servicio', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Costo del Servicio')),
                ('descripcion', models.TextField(blank=True, null=True, verbose_name='Descripción del Servicio')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name': 'Servicio Adicional',
                'verbose_name_plural': 'Servicios Adicionales',
                'ordering': ['nombre_servicio'],
            },
        ),
        migrations.CreateModel(
            name='Atencion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_atencion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Atención')),
                ('motivo_consulta', models.TextField(verbose_name='Motivo de Consulta')),
                ('tratamiento', models.TextField(verbose_name='Tratamiento')),
                ('comentario', models.TextField(blank=True, null=True, verbose_name='Comentario')),
                ('diagnostico', models.ManyToManyField(related_name='diagnosticos_atencion', to='core.diagnostico', verbose_name='Diagnósticos')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='doctores_atencion', to='core.paciente', verbose_name='Paciente')),
            ],
            options={
                'verbose_name': 'Atención',
                'verbose_name_plural': 'Atenciones',
                'ordering': ['-fecha_atencion'],
            },
        ),
        migrations.CreateModel(
            name='DetalleAtencion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(verbose_name='Cantidad')),
                ('prescripcion', models.TextField(verbose_name='Prescripción')),
                ('duracion_tratamiento', models.PositiveIntegerField(blank=True, null=True, verbose_name='Duración del Tratamiento (días)')),
                ('atencion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='atenciones', to='attention.atencion', verbose_name='Cabecera de Atención')),
                ('medicamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicamentos', to='core.medicamento', verbose_name='Medicamento')),
            ],
            options={
                'verbose_name': 'Detalle de Atención',
                'verbose_name_plural': 'Detalles de Atención',
                'ordering': ['atencion'],
            },
        ),
        migrations.CreateModel(
            name='ExamenSolicitado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_examen', models.CharField(max_length=255, verbose_name='Nombre del Examen')),
                ('fecha_solicitud', models.DateField(auto_now_add=True, verbose_name='Fecha de Solicitud')),
                ('resultado', models.FileField(blank=True, null=True, upload_to='resultados_examenes/', verbose_name='Resultado del Examen')),
                ('comentario', models.TextField(blank=True, null=True, verbose_name='Comentario')),
                ('estado', models.CharField(choices=[('S', 'Solicitado'), ('R', 'Realizado')], max_length=20, verbose_name='Estado del Examen')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pacientes_examenes', to='core.paciente', verbose_name='Paciente')),
            ],
            options={
                'verbose_name': 'Examen Médico',
                'verbose_name_plural': 'Exámenes Médicos',
                'ordering': ['-fecha_solicitud'],
            },
        ),
        migrations.CreateModel(
            name='CostosAtencion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Total')),
                ('fecha_registro', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('atencion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='costos_atencion', to='attention.atencion', verbose_name='Atención')),
                ('servicios_adicionales', models.ManyToManyField(blank=True, related_name='servicios_adicionales', to='attention.serviciosadicionales', verbose_name='Servicios Adicionales')),
            ],
            options={
                'verbose_name': 'Costo de Atención',
                'verbose_name_plural': 'Costos de Atención',
                'ordering': ['-fecha_registro'],
            },
        ),
        migrations.CreateModel(
            name='CitaMedica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(verbose_name='Fecha de la Cita')),
                ('hora_cita', models.TimeField(verbose_name='Hora de la Cita')),
                ('estado', models.CharField(choices=[('P', 'Programada'), ('C', 'Cancelada'), ('R', 'Realizada')], max_length=1, verbose_name='Estado de la Cita')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pacientes_citas', to='core.paciente', verbose_name='Paciente')),
            ],
            options={
                'verbose_name': 'Cita Médica',
                'verbose_name_plural': 'Citas Médicas',
                'ordering': ['fecha', 'hora_cita'],
                'indexes': [models.Index(fields=['fecha', 'hora_cita'], name='idx_fecha_hora')],
            },
        ),
    ]
