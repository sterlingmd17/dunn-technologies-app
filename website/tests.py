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

    def test_pricing_shows_included_services_and_request_quote_link(self):
        response = self.client.get(reverse('pricing'))
        # check that an included service label appears on the page
        self.assertContains(response, 'Helpdesk &amp; Support')
        self.assertContains(response, 'RMM &amp; Patching')
        # request-quote CTA should include services query parameter
        self.assertContains(response, '?plan=starter')
        self.assertContains(response, '&services=')


class ContactPrefillTests(TestCase):
    def test_contact_prefill_from_pricing_query(self):
        url = reverse('contact') + '?plan=standard&services=backup,security'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # the selected plan should be displayed and the services mapped to human labels
        self.assertContains(response, 'Selected plan:')
        self.assertContains(response, 'standard')
        self.assertContains(response, 'Backup &amp; Disaster Recovery')
        self.assertContains(response, 'Managed Security')

    def test_contact_post_includes_plan_and_services_in_email(self):
        data = {
            "name": "Carol",
            "company": "Acme",
            "email": "carol@acme.test",
            "phone": "555-0300",
            "message": "Please quote",
            "plan": "standard",
            "selected_services": "Backup & Disaster Recovery, Managed Security",
        }

        with self.settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
                           CONTACT_RECIPIENT_EMAIL="recipient@example.com"):
            response = self.client.post(reverse('contact'), data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(mail.outbox), 1)
            body = mail.outbox[0].body
            self.assertIn('Plan: standard', body)
            self.assertIn('Selected services: Backup & Disaster Recovery, Managed Security', body)
