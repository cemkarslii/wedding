from django.contrib import admin

# Register your models here.

from .models import MessageTypeChoices, WeddingMessage, WeddingPhoto


@admin.register(WeddingMessage)
class WeddingMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "message_type", "attendance", "created_at")
    list_filter = ("message_type", "created_at")
    search_fields = ("name", "message")
    ordering = ("-created_at",)


@admin.register(WeddingPhoto)
class WeddingPhotoAdmin(admin.ModelAdmin):
    list_display = ("image", "uploaded_at")
    ordering = ("-uploaded_at",)
