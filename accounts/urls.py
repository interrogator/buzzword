from django.urls import path

from accounts import views
from buzzword.utils import management_handling

app_name = "accounts"

if management_handling():
    urlpatterns = []
else:
    from start import views as start_views
    urlpatterns = [
        path('signup/', start_views.signup, name='signup'),
        #path("signup/", views.signup, name="signup"),
        path("logout/", views.logout_view, name="logout"),
        path("login/", views.login_view, name="login"),
        path("corpus_settings/", views.corpus_settings, name="corpus_settings"),
]
