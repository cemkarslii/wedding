from django import forms
from page.models import MessageTypeChoices, WeddingMessage


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
