from django.urls import re_path
from authentication.views import (
    RegisterView,
    LoginView,
    GoogleLoginView,
    LogoutView,
    SendRegistrationOtpView,
    SendResetOtpView,
    VerifyOtpView,
    ResetPasswordView,
)

urlpatterns = [
    # Auth
    re_path(r'^register/?$', RegisterView.as_view(), name='auth-register'),
    re_path(r'^login/?$', LoginView.as_view(), name='auth-login'),
    re_path(r'^google/?$', GoogleLoginView.as_view(), name='auth-google'),
    re_path(r'^google/token/?$', GoogleLoginView.as_view(), name='auth-google-token'),
    re_path(r'^logout/?$', LogoutView.as_view(), name='auth-logout'),

    # OTP
    re_path(r'^otp/send-registration/?$', SendRegistrationOtpView.as_view(), name='otp-send-reg'),
    re_path(r'^otp/send-reset/?$', SendResetOtpView.as_view(), name='otp-send-reset'),
    re_path(r'^otp/send-otp/?$', SendResetOtpView.as_view(), name='otp-send-otp'),
    re_path(r'^otp/verify/?$', VerifyOtpView.as_view(), name='otp-verify'),

    # Password
    re_path(r'^password/reset/?$', ResetPasswordView.as_view(), name='password-reset'),
    re_path(r'^update/?$', ResetPasswordView.as_view(), name='password-update'),
]
