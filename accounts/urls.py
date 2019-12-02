from django.urls import path

from accounts import views as accounts_views


urlpatterns = [
    path('signup/', accounts_views.signup, name='signup'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('login/', accounts_views.login_view, name='login'),
]
