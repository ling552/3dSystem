from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('me/', views.profile, name='profile'),
    path('me/edit/', views.profile_edit, name='profile_edit'),
    path(
        'me/password/',
        auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html', success_url='/me/password/done/'),
        name='password_change',
    ),
    path('me/password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('upload/', views.upload_asset, name='upload_asset'),
    path('assets/public/', views.asset_public_list, name='asset_public_list'),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/<uuid:asset_id>/', views.asset_detail, name='asset_detail'),
    path('viewer/<uuid:asset_id>/', views.viewer, name='viewer'),
    path('assets/<uuid:asset_id>/delete/', views.asset_delete, name='asset_delete'),
    path('assets/<uuid:asset_id>/download/', views.asset_download, name='asset_download'),
]
