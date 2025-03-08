from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class UserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('username', 'email')

admin.site.register(User, UserAdmin)
