from django.test import TestCase
from django.urls import reverse

from page.models import WeddingMessage


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

# Create your tests here.
