from django.urls import path
from .views import RegistrationView, ActivateAccountView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate-account'),
]