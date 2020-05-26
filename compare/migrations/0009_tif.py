# Generated by Django 3.0.6 on 2020-05-26 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compare', '0008_auto_20200526_1311'),
    ]

    operations = [
        migrations.CreateModel(
            name='TIF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=255)),
                ('path', models.TextField()),
                ('name', models.CharField(max_length=200)),
                ('num', models.IntegerField()),
            ],
            options={
                'unique_together': {('slug', 'num')},
            },
        ),
    ]
