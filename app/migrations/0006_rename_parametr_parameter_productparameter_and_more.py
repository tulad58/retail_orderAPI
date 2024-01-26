# Generated by Django 5.0.1 on 2024-01-22 12:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_productparametr_value'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Parametr',
            new_name='Parameter',
        ),
        migrations.CreateModel(
            name='ProductParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=50, verbose_name='Стоимость')),
                ('parameter', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='app.parameter', verbose_name='Параметр')),
                ('product_info', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='app.productinfo', verbose_name='Информация о продукте')),
            ],
            options={
                'verbose_name': 'Продукт и Параметр',
                'verbose_name_plural': 'Список продуктов и параметров',
            },
        ),
        migrations.DeleteModel(
            name='ProductParametr',
        ),
    ]