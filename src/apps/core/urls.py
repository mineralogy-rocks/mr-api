from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views as views


app_name = "core"

router = DefaultRouter()

router.register(r"mineral", views.MineralViewSet, basename="mineral")
router.register(r"status", views.StatusViewSet, basename="status")


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [path("", include(router.urls)), path("sentry-debug/", trigger_error)]
