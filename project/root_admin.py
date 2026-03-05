from django.contrib.admin import AdminSite


class RootAdminSite(AdminSite):
    site_header = '管理后台'
    site_title = '管理后台'
    index_title = '站点管理'

    def has_permission(self, request):
        user = request.user
        return bool(user.is_active and user.is_staff and user.username == 'root')


root_admin_site = RootAdminSite(name='root_admin')
