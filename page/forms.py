from pathlib import Path

from django import forms

from page.models import MessageTypeChoices, WeddingMessage


MAX_IMAGE_SIZE = 1024 * 1024 * 1024
MAX_MEDIA_PER_UPLOAD = 10
ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png"}


class MultipleMediaInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleMediaField(forms.FileField):
    widget = MultipleMediaInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(media, initial) for media in data]
        return [single_file_clean(data, initial)]


class WeddingPhotoUploadForm(forms.Form):
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
                if media_file.size > MAX_IMAGE_SIZE:
                    raise forms.ValidationError(
                        f"{media_file.name} dosyası 1 GB sınırını aşıyor."
                    )
                forms.ImageField().clean(media_file)
                continue

            raise forms.ValidationError("Yalnızca JPG veya PNG görsel yükleyebilirsiniz.")

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
