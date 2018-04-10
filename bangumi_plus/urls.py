"""bangumi_plus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from bangumi.views import SubjectViewSet, TokenViewSet
from recommendation.views import RecommendationDetailViewSet, RecommendationViewSet

router = routers.DefaultRouter()
router.register(r'token', TokenViewSet, base_name="token")
router.register(r'subjects', SubjectViewSet)
router.register(r'recommendations', RecommendationViewSet)
router.register(r'comments', RecommendationDetailViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
] + router.urls
