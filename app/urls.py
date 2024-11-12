from django.urls import path
from . import views

urlpatterns = [
    path("", views.analyze_views.index, name="index"),
]
