from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services, name="services"),
    path("service-area/", views.service_area, name="service_area"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]