# Generated by Django 3.1.7 on 2021-04-24 03:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0040_subeditprice'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_recommend',
            field=models.BooleanField(default=False, verbose_name='Рекомендовать'),
        ),
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.FloatField(null=True, verbose_name='Рейтинг'),
        ),
        migrations.CreateModel(
            name='RatingProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_rating', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating_product', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rating_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]