"""URL configuration for the wedding site."""

from django.urls import path

from page import views

urlpatterns = [
    path("", views.home, name="home"),
    path("send-message/", views.send_message, name="send_message"),
]
