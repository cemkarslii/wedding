import base64
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse

from page.models import WeddingMessage, WeddingPhoto


class SendMessageTests(TestCase):
    def test_home_contains_backend_connected_contact_form(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, f'action="{reverse("send_message")}"')
        self.assertContains(response, 'name="message_type"')
        self.assertContains(response, 'name="attendance"')

    def test_ajax_submission_creates_message_and_returns_json(self):
        response = self.client.post(
            reverse("send_message"),
            {
                "name": "Ada Lovelace",
                "message_type": "message",
                "message": "Mutluluklar!",
                "attendance": "",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})
        self.assertTrue(WeddingMessage.objects.filter(name="Ada Lovelace").exists())

    def test_attendance_is_required_for_attendance_status(self):
        response = self.client.post(
            reverse("send_message"),
            {
                "name": "Alan Turing",
                "message_type": "attendance_status",
                "message": "Katılım bilgim",
                "attendance": "",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("attendance", response.json()["errors"])
        self.assertFalse(WeddingMessage.objects.exists())

    def test_regular_submission_keeps_redirect_fallback(self):
        response = self.client.post(
            reverse("send_message"),
            {
                "name": "Grace Hopper",
                "message_type": "congratulations",
                "message": "Tebrikler!",
                "attendance": "",
            },
        )

        self.assertRedirects(response, reverse("home") + "#contact-form")


class UploadPhotosTests(TestCase):
    png_content = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )

    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.media_root)

    def make_photo(self, name):
        return SimpleUploadedFile(name, self.png_content, content_type="image/png")

    def test_ajax_upload_saves_multiple_photos(self):
        response = self.client.post(
            reverse("upload_photos"),
            {"photos": [self.make_photo("one.png"), self.make_photo("two.png")]},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "uploaded_count": 2})
        self.assertEqual(WeddingPhoto.objects.count(), 2)
        for photo in WeddingPhoto.objects.all():
            self.assertTrue(photo.image.storage.exists(photo.image.name))

    def test_invalid_image_is_rejected(self):
        response = self.client.post(
            reverse("upload_photos"),
            {
                "photos": SimpleUploadedFile(
                    "not-an-image.jpg", b"not an image", content_type="image/jpeg"
                )
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("photos", response.json()["errors"])
        self.assertFalse(WeddingPhoto.objects.exists())

# Create your tests here.
