from django import forms
from django.utils.html import strip_tags
import re


CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
PLAN_RE = re.compile(r"^[a-z0-9_-]{0,64}$")


def sanitize_single_line(value: str) -> str:
    if not value:
        return ""
    cleaned = strip_tags(value)
    cleaned = CONTROL_CHARS_RE.sub("", cleaned)
    cleaned = cleaned.replace("\r", " ").replace("\n", " ")
    return " ".join(cleaned.split())


def sanitize_multiline(value: str) -> str:
    if not value:
        return ""
    cleaned = strip_tags(value)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = CONTROL_CHARS_RE.sub("", cleaned)
    lines = [" ".join(line.split()) for line in cleaned.split("\n")]
    return "\n".join(line for line in lines if line).strip()

class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={"class":"form-control"}))
    company = forms.CharField(max_length=120, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class":"form-control"}))
    phone = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    message = forms.CharField(max_length=4000, widget=forms.Textarea(attrs={"class":"form-control", "rows":5, "maxlength":4000}))
    # Hidden fields to support "Request quote" pre-selection from Pricing/Services pages
    plan = forms.CharField(required=False, widget=forms.HiddenInput())
    selected_services = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_name(self):
        return sanitize_single_line(self.cleaned_data.get("name", ""))

    def clean_company(self):
        return sanitize_single_line(self.cleaned_data.get("company", ""))

    def clean_email(self):
        return self.cleaned_data.get("email", "").strip().lower()

    def clean_phone(self):
        return sanitize_single_line(self.cleaned_data.get("phone", ""))

    def clean_message(self):
        message = sanitize_multiline(self.cleaned_data.get("message", ""))
        if not message:
            raise forms.ValidationError("Please provide a message.")
        return message

    def clean_plan(self):
        plan = sanitize_single_line(self.cleaned_data.get("plan", ""))
        if plan and not PLAN_RE.match(plan):
            raise forms.ValidationError("Invalid plan value.")
        return plan

    def clean_selected_services(self):
        raw = self.cleaned_data.get("selected_services", "")
        if not raw:
            return ""
        items = [sanitize_single_line(part) for part in raw.split(",")]
        items = [part for part in items if part]
        return ", ".join(items)
