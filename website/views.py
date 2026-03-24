import logging
from smtplib import SMTPException

from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from .forms import ContactForm


logger = logging.getLogger(__name__)

# Service slug -> human label mapping used for pricing and contact prefill
SERVICE_LABELS = {
    'helpdesk': 'Helpdesk & Support',
    'security': 'Managed Security',
    'backup': 'Backup & Disaster Recovery',
    'networking': 'Networking & Infrastructure',
    'cloud': 'Cloud Services',
    'voip': 'VoIP & UC',
    'servers': 'Servers & On-prem',
}


def home(request):
    return render(request, "website/home.html")


def services(request):
    return render(request, "website/services.html")


def service_area(request):
    return render(request, "website/service_area.html")


def about(request):
    return render(request, "website/about.html")


def pricing(request):
    return render(request, "website/pricing.html")


def contact(request):
    # Support pre-filling from ?plan=...&services=a,b,c
    prefilled_plan = request.GET.get('plan') if request.method == 'GET' else None
    prefilled_services = request.GET.get('services') if request.method == 'GET' else None

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            subject_prefix = getattr(settings, "CONTACT_EMAIL_SUBJECT_PREFIX", "[Website Lead]")
            subject = f"{subject_prefix} {data['company'] or data['name']}"
            message = (
                f"Name: {data['name']}\n"
                f"Company: {data['company']}\n"
                f"Email: {data['email']}\n"
                f"Phone: {data['phone']}\n\n"
                f"Message:\n{data['message']}\n\n"
                f"Plan: {data.get('plan')}\n"
                f"Selected services: {data.get('selected_services')}"
            )

            recipient = getattr(settings, "CONTACT_RECIPIENT_EMAIL", "your_email@dunntech.com")

            if not recipient or recipient == "your_email@dunntech.com":
                messages.error(
                    request,
                    "Contact email is not configured yet. Set CONTACT_RECIPIENT_EMAIL in your environment.",
                )
                return render(request, "website/contact.html", {"form": form})

            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
                reply_to=[data["email"]],
            )

            try:
                email.send(fail_silently=False)
            except (SMTPException, OSError, ValueError) as exc:
                logger.exception("Contact form email failed: %s", exc)
                messages.error(
                    request,
                    "Your message could not be sent right now. Please verify email settings and try again.",
                )
                return render(request, "website/contact.html", {"form": form})

            messages.success(request, "Your message has been sent.")
            form = ContactForm()
            return render(request, "website/contact.html", {"form": form})
    else:
        initial = {}
        if prefilled_plan:
            initial['plan'] = prefilled_plan
        if prefilled_services:
            # map slugs to human labels where possible
            services = []
            for s in prefilled_services.split(','):
                services.append(SERVICE_LABELS.get(s, s.replace('-', ' ').title()))
            initial['selected_services'] = ', '.join(services)
        form = ContactForm(initial=initial)

    return render(request, "website/contact.html", {"form": form})