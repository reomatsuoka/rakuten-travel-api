# Generated by Django 2.2.19 on 2021-03-16 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('middle_class_name', models.CharField(max_length=20, verbose_name='都道府県名')),
                ('small_class_name', models.CharField(max_length=20, verbose_name='市名')),
                ('detail_class_name', models.CharField(blank=True, max_length=20, verbose_name='詳細地名')),
                ('checkin_date', models.DateField()),
                ('checkout_date', models.DateField()),
            ],
        ),
    ]
