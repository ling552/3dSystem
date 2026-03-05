import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def asset_upload_to(instance: 'ModelAsset', filename: str) -> str:
    user_id = instance.owner_id or 'anonymous'
    asset_id = instance.pk or 'unassigned'
    return f"models/{user_id}/{asset_id}/{filename}"


class ModelAsset(models.Model):
    class Visibility(models.TextChoices):
        PRIVATE = 'private', '私有'
        PUBLIC = 'public', '公开'
        UNLISTED = 'unlisted', '不公开（仅链接可访问）'

    class Status(models.TextChoices):
        UPLOADED = 'uploaded', '已上传'
        PROCESSING = 'processing', '处理中'
        READY = 'ready', '就绪'
        BLOCKED = 'blocked', '已禁用'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to=asset_upload_to)
    size_bytes = models.BigIntegerField(default=0)

    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PRIVATE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPLOADED)

    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


def avatar_upload_to(instance: 'UserProfile', filename: str) -> str:
    return f"avatars/{instance.user_id}/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.FileField(upload_to=avatar_upload_to, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile({self.user_id})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def _create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
