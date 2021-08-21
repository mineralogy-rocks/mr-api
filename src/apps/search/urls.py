from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import MineralLogDocumentView

router = DefaultRouter()
mineral_log = router.register(r'mineral_log',
                        MineralLogDocumentView,
                        basename='mineral-log-document')

urlpatterns = [
    url(r'^', include(router.urls)),
]
