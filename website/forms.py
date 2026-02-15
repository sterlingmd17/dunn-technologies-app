from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={"class":"form-control"}))
    company = forms.CharField(max_length=120, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class":"form-control"}))
    phone = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={"class":"form-control"}))
    message = forms.CharField(widget=forms.Textarea(attrs={"class":"form-control", "rows":5}))
    # Hidden fields to support "Request quote" pre-selection from Pricing/Services pages
    plan = forms.CharField(required=False, widget=forms.HiddenInput())
    selected_services = forms.CharField(required=False, widget=forms.HiddenInput())
