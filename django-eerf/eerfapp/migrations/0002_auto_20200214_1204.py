# Generated by Django 2.2.5 on 2020-02-14 17:04

from django.db import migrations
import eerfapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('eerfapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='alcohol_abuse',
            field=eerfapp.models.EnumField(choices=[('unknown', 'unknown'), ('no', 'no'), ('yes', 'yes')], default='unknown', max_length=104),
        ),
        migrations.AlterField(
            model_name='subject',
            name='drug_abuse',
            field=eerfapp.models.EnumField(choices=[('unknown', 'unknown'), ('no', 'no'), ('yes', 'yes')], default='unknown', max_length=104),
        ),
        migrations.AlterField(
            model_name='subject',
            name='handedness',
            field=eerfapp.models.EnumField(choices=[('unknown', 'unknown'), ('right', 'right'), ('left', 'left'), ('equal', 'equal')], default='unknown', max_length=104),
        ),
        migrations.AlterField(
            model_name='subject',
            name='heart_impairment',
            field=eerfapp.models.EnumField(choices=[('unknown', 'unknown'), ('no', 'no'), ('yes', 'yes'), ('pacemaker', 'pacemaker')], default='unknown', max_length=104),
        ),
        migrations.AlterField(
            model_name='subject',
            name='medication',
            field=eerfapp.models.EnumField(choices=[('unknown', 'unknown'), ('no', 'no'), ('yes', 'yes')], default='unknown', max_length=104),
        ),
        migrations.AlterField(
            model_name='subject',
            name='sex',
            field=eerfapp.models.EnumField(choices=[('unknown', 'unknown'), ('male', 'male'), ('female', 'female'), ('unspecified', 'unspecified')], default='unknown', max_length=104),
        ),
        migrations.AlterField(
            model_name='subject',
            name='smoking',
            field=eerfapp.models.EnumField(choices=[('unknown', 'unknown'), ('no', 'no'), ('yes', 'yes')], default='unknown', max_length=104),
        ),
        migrations.AlterField(
            model_name='subject',
            name='visual_impairment',
            field=eerfapp.models.EnumField(choices=[('unknown', 'unknown'), ('no', 'no'), ('yes', 'yes'), ('corrected', 'corrected')], default='unknown', max_length=104),
        ),
    ]