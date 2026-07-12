from django.urls import path
from .views import RegistrationView, ActivateAccountView, CookieTokenObtainPairView, CookieRefreshView, \
 LogoutView, HelloWorldView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate-account'),
    path('login/', CookieTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', CookieRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('test/', HelloWorldView.as_view(), name='test-get')
]