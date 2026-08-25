from django.db.models.signals import post_delete
from django.dispatch import receiver

from page.models import WeddingPhoto


@receiver(post_delete, sender=WeddingPhoto)
def delete_wedding_photo_file(sender, instance, **kwargs):
    """Remove the stored media file after its database record is deleted."""
    if not instance.file:
        return

    storage = instance.file.storage
    file_name = instance.file.name
    if file_name and storage.exists(file_name):
        storage.delete(file_name)
