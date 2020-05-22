from django.urls import path

from accounts import views


urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("login/", views.login_view, name="login"),
    path("corpus_settings/", views.corpus_settings, name="corpus_settings"),
]
