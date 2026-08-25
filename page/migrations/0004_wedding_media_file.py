from django.db import migrations, models


def copy_image_to_file(apps, schema_editor):
    wedding_photo = apps.get_model("page", "WeddingPhoto")
    for media in wedding_photo.objects.iterator():
        media.file = media.image.name
        media.save(update_fields=["file"])


def copy_file_to_image(apps, schema_editor):
    wedding_photo = apps.get_model("page", "WeddingPhoto")
    for media in wedding_photo.objects.iterator():
        media.image = media.file.name
        media.save(update_fields=["image"])


class Migration(migrations.Migration):
    dependencies = [
        ("page", "0003_alter_weddingphoto_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="weddingphoto",
            name="file",
            field=models.FileField(
                blank=True, null=True, upload_to="wedding_media/"
            ),
        ),
        migrations.RunPython(copy_image_to_file, copy_file_to_image),
        migrations.RemoveField(model_name="weddingphoto", name="image"),
        migrations.AlterField(
            model_name="weddingphoto",
            name="file",
            field=models.FileField(upload_to="wedding_media/"),
        ),
        migrations.AlterModelOptions(
            name="weddingphoto",
            options={
                "verbose_name": "düğün medyası",
                "verbose_name_plural": "düğün medyaları",
            },
        ),
    ]
