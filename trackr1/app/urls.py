from django.urls import path
from . import views

urlpatterns = [
    path("",views.index, name=""),
    path("signup/",views.signup, name="signup"),
    path("signin/",views.signin, name="signin"),
    path("dashboard/", views.user_dashboard, name="user_dashboard"),
    path("userlogout/", views.userlogout, name="userlogout"),
    path('userdata/', views.userdata, name='userdata'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('edit-personal-stats/', views.edit_personal_stats, name='edit_personal_stats'),
    path('contactUs/', views.contactUs, name='contactUs'),
    path('aboutUs/', views.aboutUs, name='aboutUs'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
    path('request_password/', views.request_password, name='request_password'),
    path('reset_password/<uemail>/', views.reset_password, name='reset_password'),
    path('change_password/', views.change_password, name='change_password'),
    path("bmi_calculator/", views.bmi_calculator, name="bmi_calculator"),
    path("health_stats/", views.health_stats, name="health_stats"),
    path('set-daily-target/', views.set_daily_target, name='set_daily_target'),
]
