"""
URL configuration for budget_system project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from brands.views import BrandViewSet
from campaigns.views import CampaignViewSet, DaypartingScheduleViewSet
from core.views import SpendViewSet

# API Router
router = routers.DefaultRouter()
router.register(r'brands', BrandViewSet)
router.register(r'campaigns', CampaignViewSet)
router.register(r'dayparting-schedules', DaypartingScheduleViewSet)
router.register(r'spend', SpendViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
] 