from django.contrib import admin

# Register your models here.
from bangumi.models import UserInfo
from recommendation.models import RecommendationDetail


@admin.register(RecommendationDetail)
class RecommendationDetailAdmin(admin.ModelAdmin):
    pass


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    pass
