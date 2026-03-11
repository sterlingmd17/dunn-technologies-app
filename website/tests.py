from django.test import TestCase
from django.urls import reverse
from django.core import mail
from unittest.mock import patch

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

    def test_contact_form_sanitizes_html_and_control_chars(self):
        data = {
            "name": "<b>Alice</b>\r\n",
            "company": "<script>alert(1)</script> Example Co",
            "email": "ALICE@EXAMPLE.COM",
            "phone": " 555-0100 \n",
            "message": "<p>Hello</p>\r\n<script>bad()</script>Need support\x07",
            "plan": "per_user",
            "selected_services": "security,<b>backup</b>",
        }
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data
        self.assertEqual(cleaned["name"], "Alice")
        self.assertEqual(cleaned["company"], "alert(1) Example Co")
        self.assertEqual(cleaned["email"], "alice@example.com")
        self.assertEqual(cleaned["phone"], "555-0100")
        self.assertEqual(cleaned["message"], "Hello\nbad()Need support")
        self.assertEqual(cleaned["selected_services"], "security, backup")


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
            self.assertIn("Website Lead", mail.outbox[0].subject)

    def test_post_handles_email_send_failure_gracefully(self):
        data = {
            "name": "Bob Tester",
            "company": "Testers Inc",
            "email": "bob@test.com",
            "phone": "555-0200",
            "message": "This is a test lead.",
        }

        with self.settings(CONTACT_RECIPIENT_EMAIL="recipient@example.com"):
            with patch("website.views.EmailMessage.send", side_effect=OSError("SMTP unavailable")):
                response = self.client.post(reverse("contact"), data)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "could not be sent right now")

    def test_post_shows_config_error_when_contact_recipient_missing(self):
        data = {
            "name": "Bob Tester",
            "company": "Testers Inc",
            "email": "bob@test.com",
            "phone": "555-0200",
            "message": "This is a test lead.",
        }

        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
            CONTACT_RECIPIENT_EMAIL="your_email@dunntech.com",
        ):
            response = self.client.post(reverse("contact"), data)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Contact email is not configured yet")
            self.assertEqual(len(mail.outbox), 0)

    def test_post_sends_sanitized_email_content(self):
        data = {
            "name": "Bob\r\n",
            "company": "<b>Testers Inc</b>",
            "email": "BOB@TEST.COM",
            "phone": "555-0200\n",
            "message": "<script>x()</script>Need help",
            "selected_services": "security,<b>backup</b>",
        }

        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
                           CONTACT_RECIPIENT_EMAIL="recipient@example.com"):
            response = self.client.post(reverse("contact"), data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(mail.outbox), 1)
            sent = mail.outbox[0]
            self.assertNotIn("<b>", sent.subject)
            self.assertIn("Testers Inc", sent.subject)
            self.assertIn("Email: bob@test.com", sent.body)
            self.assertIn("Phone: 555-0200", sent.body)
            self.assertIn("Message:\nx()Need help", sent.body)
            self.assertIn("Selected services: security, backup", sent.body)


class PricingPageTests(TestCase):
    def test_pricing_page_renders_and_contains_tiers(self):
        response = self.client.get(reverse('pricing'))
        self.assertEqual(response.status_code, 200)
        # single per-user tier available
        self.assertContains(response, 'Per User')
        self.assertContains(response, '$150')

    def test_pricing_shows_features_and_request_link(self):
        response = self.client.get(reverse('pricing'))
        self.assertContains(response, 'All services included')
        self.assertContains(response, '24/7 helpdesk')
        self.assertContains(response, 'Security monitoring')
        self.assertContains(response, 'Backup, replication')
        self.assertContains(response, 'No contract')
        # calculator was commented out; ensure page still shows plan link
        self.assertContains(response, '?plan=per_user')
        # link should include the plan identifier
        self.assertContains(response, '?plan=per_user')


class ContactPrefillTests(TestCase):
    def test_contact_prefill_from_pricing_query(self):
        url = reverse('contact') + '?plan=per_user'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Selected plan:')
        self.assertContains(response, 'per_user')

    def test_contact_post_includes_plan_and_services_in_email(self):
        data = {
            "name": "Carol",
            "company": "Acme",
            "email": "carol@acme.test",
            "phone": "555-0300",
            "message": "Please quote",
            "plan": "per_user",
            "selected_services": "",
        }

        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
                           CONTACT_RECIPIENT_EMAIL="recipient@example.com"):
            response = self.client.post(reverse('contact'), data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(mail.outbox), 1)
            body = mail.outbox[0].body
            self.assertIn('Plan: per_user', body)
            self.assertIn('Selected services: ', body)
