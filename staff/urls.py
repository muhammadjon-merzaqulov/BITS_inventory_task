from django.urls import path
from . import views

urlpatterns = [
    path('kpi/', views.kpi_dashboard, name='kpi_dashboard'),
    path('profile/<int:pk>/', views.staff_profile, name='staff_profile'),
]
