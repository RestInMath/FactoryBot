from django.urls import path

from .views import index, SignUpView, Update

urlpatterns = [
    path("", index, name="index"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("update/", Update.as_view(), name="update"),
]
