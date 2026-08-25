import base64
import io
import shutil
import tempfile
import zipfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
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

    def make_video(self, name="video.mp4"):
        content = b"\x00\x00\x00\x18ftypisom" + (b"\x00" * 24)
        return SimpleUploadedFile(name, content, content_type="video/mp4")

    def test_ajax_upload_saves_multiple_photos(self):
        response = self.client.post(
            reverse("upload_photos"),
            {
                "media_files": [
                    self.make_photo("one.png"),
                    self.make_photo("two.png"),
                ]
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True, "uploaded_count": 2})
        self.assertEqual(WeddingPhoto.objects.count(), 2)
        for photo in WeddingPhoto.objects.all():
            self.assertTrue(photo.file.storage.exists(photo.file.name))

    def test_ajax_upload_accepts_video(self):
        response = self.client.post(
            reverse("upload_photos"),
            {"media_files": self.make_video()},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        media = WeddingPhoto.objects.get()
        self.assertTrue(media.is_video)
        self.assertTrue(media.file.storage.exists(media.file.name))

    def test_invalid_image_is_rejected(self):
        response = self.client.post(
            reverse("upload_photos"),
            {
                "media_files": SimpleUploadedFile(
                    "not-an-image.jpg", b"not an image", content_type="image/jpeg"
                )
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("media_files", response.json()["errors"])
        self.assertFalse(WeddingPhoto.objects.exists())

    def test_admin_photo_views_include_thumbnail_and_view_switcher(self):
        admin_user = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="password"
        )
        self.client.force_login(admin_user)
        photo = WeddingPhoto.objects.create(file=self.make_photo("preview.png"))
        WeddingPhoto.objects.create(file=self.make_video("preview.mp4"))

        list_response = self.client.get(
            reverse("admin:page_weddingphoto_changelist")
        )
        detail_response = self.client.get(
            reverse("admin:page_weddingphoto_change", args=[photo.pk])
        )

        self.assertContains(list_response, "wedding-photo-thumbnail")
        self.assertContains(list_response, "wedding-video-thumbnail")
        self.assertContains(list_response, 'data-media-type="image"')
        self.assertContains(list_response, 'data-media-type="video"')
        self.assertContains(list_response, "media-preview-primary")
        self.assertContains(list_response, "media-zoom-button")
        self.assertContains(list_response, "Medya türü")
        self.assertContains(list_response, "Dosya boyutu")
        self.assertContains(list_response, f"{len(self.png_content)} B")
        self.assertContains(list_response, 'data-photo-view="list"')
        self.assertContains(list_response, 'data-photo-view="grid"')
        self.assertContains(list_response, "data-select-all-photos")
        self.assertContains(list_response, "data-download-selected")
        self.assertContains(detail_response, "wedding-photo-large-preview")

        video_response = self.client.get(
            reverse("admin:page_weddingphoto_changelist") + "?media_type=video"
        )
        video = WeddingPhoto.objects.get(file__iendswith="preview.mp4")
        self.assertContains(
            video_response,
            reverse("admin:page_weddingphoto_change", args=[video.pk]),
        )
        self.assertNotContains(
            video_response,
            reverse("admin:page_weddingphoto_change", args=[photo.pk]),
        )

    def test_deleting_photo_record_removes_stored_file(self):
        photo = WeddingPhoto.objects.create(file=self.make_photo("delete-me.png"))
        storage = photo.file.storage
        image_name = photo.file.name

        self.assertTrue(storage.exists(image_name))
        photo.delete()

        self.assertFalse(storage.exists(image_name))

    def test_admin_can_download_all_selected_photos_as_zip(self):
        admin_user = get_user_model().objects.create_superuser(
            username="zip-admin", email="zip@example.com", password="password"
        )
        self.client.force_login(admin_user)
        first = WeddingPhoto.objects.create(file=self.make_photo("first.png"))
        second = WeddingPhoto.objects.create(file=self.make_video("second.mp4"))

        response = self.client.post(
            reverse("admin:page_weddingphoto_changelist"),
            {
                "action": "download_selected_photos",
                "_selected_action": [first.pk],
                "select_across": "1",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        archive_content = b"".join(response.streaming_content)
        response.close()
        with zipfile.ZipFile(io.BytesIO(archive_content)) as archive:
            archived_names = archive.namelist()
        self.assertEqual(len(archived_names), 2)
        self.assertTrue(any(name.endswith("first.png") for name in archived_names))
        self.assertTrue(any(name.endswith("second.mp4") for name in archived_names))

# Create your tests here.
