from django import forms
from page.models import MessageTypeChoices, WeddingMessage


MAX_PHOTO_SIZE = 10 * 1024 * 1024
MAX_PHOTOS_PER_UPLOAD = 10
ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png"}


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        single_image_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_image_clean(image, initial) for image in data]
        return [single_image_clean(data, initial)]


class WeddingPhotoUploadForm(forms.Form):
    photos = MultipleImageField()

    def clean_photos(self):
        photos = self.cleaned_data["photos"]
        if len(photos) > MAX_PHOTOS_PER_UPLOAD:
            raise forms.ValidationError(
                f"Tek seferde en fazla {MAX_PHOTOS_PER_UPLOAD} fotoğraf yükleyebilirsiniz."
            )

        for photo in photos:
            if photo.size > MAX_PHOTO_SIZE:
                raise forms.ValidationError(
                    f"{photo.name} dosyası 10 MB sınırını aşıyor."
                )
            if photo.content_type not in ALLOWED_PHOTO_TYPES:
                raise forms.ValidationError("Yalnızca JPG ve PNG yükleyebilirsiniz.")
        return photos


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
