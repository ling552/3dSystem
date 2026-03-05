from django.contrib import admin

from project.root_admin import root_admin_site

from .models import ModelAsset, UserProfile


class ModelAssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'visibility', 'status', 'created_at', 'deleted_at')
    list_filter = ('visibility', 'status')
    search_fields = ('name', 'original_filename', 'id', 'owner__username')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'updated_at')


root_admin_site.register(ModelAsset, ModelAssetAdmin)
root_admin_site.register(UserProfile, UserProfileAdmin)
