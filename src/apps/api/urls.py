from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views as views

app_name = 'api'



router = DefaultRouter()

router.register(r'mineral', views.MineralViewSet, basename='mineral')
router.register(r'status', views.StatusViewSet, basename='status')

urlpatterns = [
    path('', include(router.urls)),
]

# urlpatterns = [
#     path('mineral/<uuid:pk>', views.mineral_basic.as_view(), name='mineral'),
#     path('mineral/history/<uuid:pk>', views.mineral_history.as_view(), name='mineral_history'),
#     path('mineral/relation/<uuid:pk>', views.mineral_relation.as_view(), name='mineral_relation'),
#     path('mineral/classification/<uuid:pk>', views.mineralClassification.as_view(), name='mineral_classification'),
#     path('group_first_children/<uuid:pk>', views.group_first_children.as_view(), name='group_first_children'),
# ]