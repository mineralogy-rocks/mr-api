from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path('status_counts', views.statusCounts.as_view(), name='status_counts'),
    path('discovery_year_counts', views.discoveryYearCounts.as_view(), name='discovery_year_counts'),
    path('discovery_country_counts', views.discoveryCountryCounts.as_view(), name='discovery_country_counts'),
]