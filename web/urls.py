from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage.as_view(), name='home'),
    path('mineral_stats', views.mineral_stats.as_view(), name='mineral_stats'),
    path('contact', views.contact.as_view(), name='contact'),
    path('about', views.about.as_view(), name='about'),
    path('api', views.api.as_view(), name='api'),
]