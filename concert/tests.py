from unittest.mock import Mock, patch
from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Concert, ConcertAttending


class BandWebsiteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testlistener", password="local-demo-pass")
        self.concert = Concert.objects.create(concert_name="Autumn live", duration=2, city="Almaty", date=date(2026, 11, 9))

    def test_home_and_protected_pages(self):
        self.assertEqual(self.client.get(reverse("index")).status_code, 200)
        self.assertRedirects(self.client.get(reverse("concerts")), reverse("login"))

    def test_signup_and_duplicate_username(self):
        response = self.client.post(reverse("signup"), {"username": "newlistener", "password": "test-demo-pass"})
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(User.objects.get(username="newlistener").check_password("test-demo-pass"))
        self.client.get(reverse("logout"))
        response = self.client.post(reverse("signup"), {"username": "newlistener", "password": "another-demo-pass"})
        self.assertContains(response, "already registered")
        self.assertEqual(User.objects.filter(username="newlistener").count(), 1)

    def test_login_and_logout(self):
        response = self.client.post(reverse("login"), {"username": "testlistener", "password": "local-demo-pass"})
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(self.client.get(reverse("concerts")).status_code, 200)
        self.client.get(reverse("logout"))
        self.assertRedirects(self.client.get(reverse("concerts")), reverse("login"))

    def test_attendance_is_scoped_to_current_user(self):
        self.client.force_login(self.user)
        other = User.objects.create_user(username="anotherlistener", password="other-demo-pass")
        for value in ["Attending", "Not Attending"]:
            self.client.post(reverse("concert_attendee"), {"concert_id": self.concert.id, "attendee_choice": value, "user": other.id})
        self.assertEqual(ConcertAttending.objects.get(user=self.user).attending, "Not Attending")
        self.assertFalse(ConcertAttending.objects.filter(user=other).exists())
        self.assertEqual(ConcertAttending.objects.count(), 1)

    def test_invalid_attendance_and_unknown_concert(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse("concert_attendee"), {"concert_id": self.concert.id, "attendee_choice": "invalid"}).status_code, 400)
        self.assertEqual(self.client.get(reverse("concert_detail", args=[9999])).status_code, 404)

    @patch("concert.views.req.get")
    def test_services_render_real_response_data(self, get):
        get.return_value = Mock(json=lambda: [{"id": 1, "title": "A live song", "lyrics": "A verse"}])
        self.assertContains(self.client.get(reverse("songs")), "A live song")
        get.return_value = Mock(json=lambda: [{"id": 1, "pic_url": "https://example.test/picture.png", "event_city": "Almaty"}])
        self.assertContains(self.client.get(reverse("photos")), "Almaty")

    @patch("concert.views.req.get")
    def test_service_outage_is_reported(self, get):
        import requests
        get.side_effect = requests.ConnectionError("Unavailable")
        self.assertEqual(self.client.get(reverse("songs")).status_code, 503)
