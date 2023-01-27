# -*- coding: UTF-8 -*-
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views as views

app_name = "bond"

router = DefaultRouter()

# router.register(r"svg", views.SVGView, basename="svg")


urlpatterns = [
    path("", include(router.urls)),
    path("svg/", views.SVGView.as_view(), name="svg")
]
