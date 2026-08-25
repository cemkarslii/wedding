import shutil
import tempfile
import zipfile
from pathlib import Path

from django.contrib import admin
from django.db.models import Q
from django.http import FileResponse
from django.utils import timezone
from django.utils.html import format_html

from .models import WeddingMessage, WeddingPhoto


class MediaTypeFilter(admin.SimpleListFilter):
    title = "Medya türü"
    parameter_name = "media_type"

    def lookups(self, request, model_admin):
        return (("photo", "Fotoğraf"), ("video", "Video"))

    def queryset(self, request, queryset):
        video_query = (
            Q(file__iendswith=".mp4")
            | Q(file__iendswith=".mov")
            | Q(file__iendswith=".webm")
        )
        if self.value() == "video":
            return queryset.filter(video_query)
        if self.value() == "photo":
            return queryset.exclude(video_query)
        return queryset


@admin.register(WeddingMessage)
class WeddingMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "message_type", "attendance", "created_at")
    list_filter = ("message_type", "created_at")
    search_fields = ("name", "message")
    ordering = ("-created_at",)


@admin.register(WeddingPhoto)
class WeddingPhotoAdmin(admin.ModelAdmin):
    change_list_template = "admin/page/weddingphoto/change_list.html"
    list_display = (
        "thumbnail",
        "media_type",
        "file_size",
        "uploaded_at",
    )
    list_display_links = ("uploaded_at",)
    readonly_fields = ("large_preview", "file_size", "uploaded_at")
    fields = ("large_preview", "file", "file_size", "uploaded_at")
    search_fields = ("file",)
    list_filter = (MediaTypeFilter,)
    actions = ("download_selected_photos",)
    list_per_page = 24
    ordering = ("-uploaded_at",)

    @admin.action(description="Seçilen dosyaları ZIP olarak indir")
    def download_selected_photos(self, request, queryset):
        archive_file = tempfile.NamedTemporaryFile(
            prefix="wedding-media-", suffix=".zip", mode="w+b"
        )

        with zipfile.ZipFile(
            archive_file, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            for photo in queryset.iterator():
                if not photo.file:
                    continue
                storage = photo.file.storage
                file_name = photo.file.name
                if not storage.exists(file_name):
                    continue

                archive_name = f"{photo.pk}_{Path(file_name).name}"
                with storage.open(file_name, "rb") as source:
                    with archive.open(archive_name, "w") as target:
                        shutil.copyfileobj(source, target)

        archive_file.seek(0)
        timestamp = timezone.localtime().strftime("%Y%m%d-%H%M")
        return FileResponse(
            archive_file,
            as_attachment=True,
            filename=f"wedding-media-{timestamp}.zip",
            content_type="application/zip",
        )

    @admin.display(description="Önizleme", ordering="file")
    def thumbnail(self, obj):
        if not obj.file:
            return "—"
        if obj.is_video:
            return format_html(
                '<div class="media-thumbnail-wrapper">'
                '<button type="button" class="media-preview-primary" data-media-url="{}" '
                'data-media-type="video" aria-label="{} videosunu seç veya büyüt">'
                '<video src="{}" class="wedding-photo-thumbnail wedding-video-thumbnail" '
                'muted playsinline preload="metadata"></video></button>'
                '<button type="button" class="media-dialog-trigger media-zoom-button" '
                'data-media-url="{}" data-media-type="video" aria-label="Videoyu büyüt">⛶</button>'
                '</div>',
                obj.file.url,
                Path(obj.file.name).name,
                obj.file.url,
                obj.file.url,
            )
        return format_html(
            '<div class="media-thumbnail-wrapper">'
            '<button type="button" class="media-preview-primary" data-media-url="{}" '
            'data-media-type="image" aria-label="{} görselini seç veya büyüt">'
            '<img src="{}" class="wedding-photo-thumbnail" alt="{}"></button>'
            '<button type="button" class="media-dialog-trigger media-zoom-button" '
            'data-media-url="{}" data-media-type="image" aria-label="Görseli büyüt">⛶</button>'
            '</div>',
            obj.file.url,
            Path(obj.file.name).name,
            obj.file.url,
            Path(obj.file.name).name,
            obj.file.url,
        )

    @admin.display(description="Tür")
    def media_type(self, obj):
        return "Video" if obj.is_video else "Fotoğraf"

    @admin.display(description="Dosya boyutu")
    def file_size(self, obj):
        if not obj or not obj.file:
            return "—"
        try:
            size = obj.file.size
        except (OSError, ValueError, NotImplementedError):
            return "—"

        units = ("B", "KB", "MB", "GB")
        value = float(size)
        for unit in units:
            if value < 1024 or unit == units[-1]:
                return f"{int(value)} {unit}" if unit == "B" else f"{value:.1f} {unit}"
            value /= 1024

    @admin.display(description="Medya önizlemesi")
    def large_preview(self, obj):
        if not obj or not obj.file:
            return "Dosya henüz yüklenmedi."
        if obj.is_video:
            return format_html(
                '<button type="button" class="media-dialog-trigger media-dialog-trigger-large" '
                'data-media-url="{}" data-media-type="video" aria-label="{} videosunu büyüt">'
                '<video src="{}" class="wedding-photo-large-preview" '
                'muted playsinline preload="metadata"></video></button>',
                obj.file.url,
                Path(obj.file.name).name,
                obj.file.url,
            )
        return format_html(
            '<button type="button" class="media-dialog-trigger media-dialog-trigger-large" '
            'data-media-url="{}" data-media-type="image" aria-label="{} görselini büyüt">'
            '<img src="{}" class="wedding-photo-large-preview" alt="{}"></button>',
            obj.file.url,
            Path(obj.file.name).name,
            obj.file.url,
            Path(obj.file.name).name,
        )

    class Media:
        css = {"all": ("admin/css/wedding_photos.css",)}
        js = ("admin/js/wedding_photos.js",)
