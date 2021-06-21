from django.urls import path, include
from . import views

app_name = 'api'

urlpatterns = [
    path('mineral/<uuid:pk>', views.mineral_basic.as_view(), name='mineral'),
    path('mineral/history/<uuid:pk>', views.mineral_history.as_view(), name='mineral_history'),
    path('mineral/relation/<uuid:pk>', views.mineral_relation.as_view(), name='mineral_relation'),
    path('mineral/classification/<uuid:pk>', views.mineralClassification.as_view(), name='mineral_classification'),
    path('group_first_children/<uuid:pk>', views.group_first_children.as_view(), name='group_first_children'),
]