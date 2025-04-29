from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views



urlpatterns = [
    path("", views.landing_page, name="landing"),  # Landing Page
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Form submission and document verification
    path("apply/", views.submit_application, name="submit_application"),  # Form submission page
    path("verify_document/<int:applicant_id>/", views.verify_document, name="verify_document"),  # Document verification page

    # Results Page for a specific applicant (with applicant_id)
    path("results/<int:applicant_id>/", views.applicant_results, name="applicant_results"),
    path("view_results/<int:result_id>/", views.view_result, name="view_result"),

    # Applicant Dashboard (Can either be specific or generic)
    path("dashboard/", views.applicant_dashboard, name="applicant_dashboard"),  # Default dashboard for logged-in user

    #forget password urls
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),
    
    path('features/', views.features_page, name='features'),
    path('contact/', views.contact_page, name='contact'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)