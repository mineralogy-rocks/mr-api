from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import MineralListDocumentView

router = DefaultRouter()
mineral_list = router.register(r'mineral_list',
                        MineralListDocumentView,
                        basename='minerallistdocument')

urlpatterns = [
    url(r'^', include(router.urls)),
]
