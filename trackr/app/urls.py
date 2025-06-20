from django.urls import path
from . import views

urlpatterns = [
    path("",views.index, name=""),
    path("signup/",views.signup, name="signup"),
    path("signin/",views.signin, name="signin"),
    path("dashboard/", views.user_dashboard, name="user_dashboard"),
    path("userlogout/", views.userlogout, name="userlogout"),
    path("workspace/", views.dietician_workspace, name="dietician_workspace"),
]
