from django.contrib import admin
from .models import (
    CustomUser,
    UserProfile,
    DieticianProfile,
    HealthLog,
    Appointment,
)
from django.contrib.auth.admin import UserAdmin


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    def get_list_display(self, request):
        return [field.name for field in CustomUser._meta.fields]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in UserProfile._meta.fields]


@admin.register(DieticianProfile)
class DieticianProfileAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in DieticianProfile._meta.fields]


@admin.register(HealthLog)
class HealthLogAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in HealthLog._meta.fields]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in Appointment._meta.fields]


admin.site.site_header = "Trackr Admin"
admin.site.site_title = "Trackr"
admin.site.index_title = "Admin Dashboard"
