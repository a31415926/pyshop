# Generated by Django 3.1.7 on 2021-04-04 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20210404_0344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='is_answer_support',
            field=models.BooleanField(default=True, verbose_name='Уведомления об ответе службы поддержки'),
        ),
        migrations.AlterField(
            model_name='subscribe',
            name='is_create_order',
            field=models.BooleanField(default=False, verbose_name='Офорлмение заказа'),
        ),
        migrations.AlterField(
            model_name='subscribe',
            name='is_promo',
            field=models.BooleanField(default=False, verbose_name='Акции'),
        ),
    ]