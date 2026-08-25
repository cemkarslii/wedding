from django.contrib import admin

# Register your models here.

from .models import WeddingMessage, MessageTypeChoices


@admin.register(WeddingMessage)
class WeddingMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "message_type", "attendance", "created_at")
    list_filter = ("message_type", "created_at")
    search_fields = ("name", "message")
    ordering = ("-created_at",)
