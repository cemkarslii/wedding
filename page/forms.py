from pathlib import Path

from django import forms

from page.models import MessageTypeChoices, WeddingMessage


MAX_PHOTO_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024
MAX_MEDIA_PER_UPLOAD = 10
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png"}
ALLOWED_VIDEO_TYPES = {
    "video/mp4": {".mp4", ".mov"},
    "video/quicktime": {".mov"},
    "video/webm": {".webm"},
}


class MultipleMediaInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleMediaField(forms.FileField):
    widget = MultipleMediaInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(media, initial) for media in data]
        return [single_file_clean(data, initial)]


class WeddingMediaUploadForm(forms.Form):
    media_files = MultipleMediaField()

    def clean_media_files(self):
        media_files = self.cleaned_data["media_files"]
        if len(media_files) > MAX_MEDIA_PER_UPLOAD:
            raise forms.ValidationError(
                f"Tek seferde en fazla {MAX_MEDIA_PER_UPLOAD} dosya yükleyebilirsiniz."
            )

        for media_file in media_files:
            content_type = media_file.content_type
            extension = Path(media_file.name).suffix.lower()

            if content_type in ALLOWED_IMAGE_TYPES:
                allowed_extension = ALLOWED_IMAGE_TYPES[content_type]
                jpeg_extensions = {".jpg", ".jpeg"}
                extension_is_valid = (
                    extension in jpeg_extensions
                    if allowed_extension == ".jpg"
                    else extension == allowed_extension
                )
                if not extension_is_valid:
                    raise forms.ValidationError("Görsel uzantısı dosya türüyle eşleşmiyor.")
                if media_file.size > MAX_PHOTO_SIZE:
                    raise forms.ValidationError(
                        f"{media_file.name} dosyası 10 MB sınırını aşıyor."
                    )
                forms.ImageField().clean(media_file)
                continue

            if content_type in ALLOWED_VIDEO_TYPES:
                if extension not in ALLOWED_VIDEO_TYPES[content_type]:
                    raise forms.ValidationError("Video uzantısı dosya türüyle eşleşmiyor.")
                if media_file.size > MAX_VIDEO_SIZE:
                    raise forms.ValidationError(
                        f"{media_file.name} dosyası 100 MB sınırını aşıyor."
                    )
                header = media_file.read(12)
                media_file.seek(0)
                is_iso_video = extension in {".mp4", ".mov"} and header[4:8] == b"ftyp"
                is_webm = extension == ".webm" and header[:4] == b"\x1aE\xdf\xa3"
                if not (is_iso_video or is_webm):
                    raise forms.ValidationError(f"{media_file.name} geçerli bir video değil.")
                continue

            raise forms.ValidationError(
                "Yalnızca JPG, PNG, MP4, MOV veya WebM yükleyebilirsiniz."
            )

        return media_files


class WeddingMessageForm(forms.ModelForm):
    class Meta:
        model = WeddingMessage
        fields = ["name", "message_type", "message", "attendance"]
        widgets = {
            "message_type": forms.Select(attrs={"aria-label": "Mesaj türü"}),
            "name": forms.TextInput(attrs={"placeholder": "Adınız Soyadınız"}),
            "attendance": forms.TextInput(
                attrs={"placeholder": "Katılım durumunuz (ör: 2 kişi katılacağız)"}
            ),
            "message": forms.Textarea(
                attrs={"placeholder": "Mesajınız...", "rows": 4}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data.get("message_type") == MessageTypeChoices.ATTENDANCE_STATUS
            and not cleaned_data.get("attendance")
        ):
            self.add_error("attendance", "Lütfen katılım durumunuzu belirtin.")
        return cleaned_data
