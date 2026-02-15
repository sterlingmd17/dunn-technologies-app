from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .forms import ContactForm

# Service slug -> human label mapping used for pricing and contact prefill
SERVICE_LABELS = {
    'networking': 'Networking & VoIP',
    'email': 'Email & Collaboration',
    'voip': 'VoIP & UC',
    'security': 'Managed Security',
    'backup': 'Backup & Disaster Recovery',
    'cloud': 'Cloud & Migration',
    'rmm': 'RMM & Patching',
    'helpdesk': 'Helpdesk & Support',
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
    # sample tiers — adjust content/prices as you like
    tiers = [
        {
            "id": "starter",
            "name": "Starter",
            "price_month": 199,
            "price_year": 1890,
            "features": ["Remote support (business hours)", "Monthly patching", "Email helpdesk"],
            "included_services": [SERVICE_LABELS['helpdesk'], SERVICE_LABELS['rmm'], SERVICE_LABELS['email']],
            "services_param": "helpdesk,rmm,email",
            "highlight": False,
        },
        {
            "id": "standard",
            "name": "Standard",
            "price_month": 499,
            "price_year": 4790,
            "features": ["24/7 monitoring", "Quarterly onsite visit", "VoIP & network support"],
            "included_services": [SERVICE_LABELS['helpdesk'], SERVICE_LABELS['rmm'], SERVICE_LABELS['email'], SERVICE_LABELS['backup'], SERVICE_LABELS['security'], SERVICE_LABELS['networking']],
            "services_param": "helpdesk,rmm,email,backup,security,networking",
            "highlight": True,
        },
        {
            "id": "enterprise",
            "name": "Enterprise",
            "price_month": 1299,
            "price_year": 12490,
            "features": ["Dedicated engineer", "SLA & priority response", "Multi-site support"],
            "included_services": [SERVICE_LABELS['helpdesk'], SERVICE_LABELS['rmm'], SERVICE_LABELS['email'], SERVICE_LABELS['backup'], SERVICE_LABELS['security'], SERVICE_LABELS['networking'], SERVICE_LABELS['cloud']],
            "services_param": "helpdesk,rmm,email,backup,security,networking,cloud",
            "highlight": False,
        },
    ]
    return render(request, "website/pricing.html", {"tiers": tiers})


def contact(request):
    # Support pre-filling from ?plan=...&services=a,b,c
    prefilled_plan = request.GET.get('plan') if request.method == 'GET' else None
    prefilled_services = request.GET.get('services') if request.method == 'GET' else None

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            subject = f"New Lead - {data['company'] or data['name']}"
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

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )

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