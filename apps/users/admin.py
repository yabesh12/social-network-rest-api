from django.contrib import admin

from apps.users.models import CustomUser, FriendRequest

# Register your models here.
@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ("status",)
    list_display = ("id", "created_at")
    ordering = ("-id",)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username")
    ordering = ("-id",)