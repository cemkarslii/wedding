from django.db import models


class MessageTypeChoices(models.TextChoices):
    CONGRATULATIONS = "congratulations", "Tebrik Mesajı"
    MESSAGE = "message", "Mesaj"
    ATTENDANCE_STATUS = "attendance_status", "Katılım Durumu"


class WeddingMessage(models.Model):
    message_type = models.CharField(
        max_length=50,
        choices=MessageTypeChoices.choices,
        default=MessageTypeChoices.CONGRATULATIONS,
    )
    name = models.CharField(max_length=100)
    message = models.TextField()
    attendance = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}: {self.message[:50]}..."


class WeddingPhoto(models.Model):
    image = models.ImageField(upload_to="wedding_photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name
