from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .forms import ContactForm

def home(request):
    return render(request, "website/home.html")

def services(request):
    return render(request, "website/services.html")

def service_area(request):
    return render(request, "website/service_area.html")

def about(request):
    return render(request, "website/about.html")

def contact(request):
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
                f"Message:\n{data['message']}"
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
        form = ContactForm()

    return render(request, "website/contact.html", {"form": form})