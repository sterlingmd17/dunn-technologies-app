from django.test import TestCase
from django.urls import reverse
from django.core import mail

from .forms import ContactForm


class ContactFormTests(TestCase):
    def test_contact_form_valid(self):
        data = {
            "name": "Alice Example",
            "company": "Example Co",
            "email": "alice@example.com",
            "phone": "555-0100",
            "message": "Please contact me about managed IT.",
        }
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())


class ContactViewTests(TestCase):
    def test_post_sends_email_and_shows_success_message(self):
        data = {
            "name": "Bob Tester",
            "company": "Testers Inc",
            "email": "bob@test.com",
            "phone": "555-0200",
            "message": "This is a test lead.",
        }

        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
                           CONTACT_RECIPIENT_EMAIL="recipient@example.com"):
            response = self.client.post(reverse("contact"), data)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Your message has been sent.")

            # one email was sent to the configured recipient
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to, ["recipient@example.com"])
            self.assertIn("New Lead", mail.outbox[0].subject)


class PricingPageTests(TestCase):
    def test_pricing_page_renders_and_contains_tiers(self):
        response = self.client.get(reverse('pricing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Starter')
        self.assertContains(response, 'Standard')
        self.assertContains(response, 'Enterprise')
