from .models import UserProfile


class EnsureUserProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and getattr(user, 'is_authenticated', False):
            try:
                _ = user.profile
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=user)
        return self.get_response(request)
