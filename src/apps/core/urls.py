# -*- coding: UTF-8 -*-
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView

from . import views as views

app_name = "core"
router = DefaultRouter()

router.register(r"nickel-strunz", views.NickelStrunzViewSet, basename="nickel-strunz")
router.register(r"mineral", views.MineralViewSet, basename="mineral")
router.register(r"relation", views.RelationViewSet, basename="relation")
router.register(r"status", views.StatusViewSet, basename="status")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("mineral-search/", views.MineralSearch.as_view(), name="mineral-search"),
]
