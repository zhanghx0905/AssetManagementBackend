# Generated by Django 2.2.4 on 2020-11-07 09:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('asset', '0003_auto_20201105_1601'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RequireIssue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('DOING', '进行中'), ('SUCCESS', '成功'), ('FAIL', '失败')], default='DOING', max_length=10)),
                ('asset', models.ManyToManyField(related_name='被领用资产', to='asset.Asset')),
                ('asset_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='领用资产类型', to='asset.AssetCategory')),
                ('handler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issue_requireissue_hanlder', to=settings.AUTH_USER_MODEL, verbose_name='处理者')),
                ('initiator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issue_requireissue_initiator', to=settings.AUTH_USER_MODEL, verbose_name='发起者')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('DOING', '进行中'), ('SUCCESS', '成功'), ('FAIL', '失败')], default='DOING', max_length=10)),
                ('type_name', models.CharField(choices=[('REQUIRE', '领用'), ('MAINTAIN', '维修'), ('TRANSFER', '转移'), ('RETURN', '退库')], max_length=10)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asset.Asset', verbose_name='资产')),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assignee', to=settings.AUTH_USER_MODEL, verbose_name='被分配者')),
                ('handler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issue_issue_hanlder', to=settings.AUTH_USER_MODEL, verbose_name='处理者')),
                ('initiator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issue_issue_initiator', to=settings.AUTH_USER_MODEL, verbose_name='发起者')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
