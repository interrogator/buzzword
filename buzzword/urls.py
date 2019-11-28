from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as accounts_views

urlpatterns = [
    path('', include("start.urls")),
    path('signup/', accounts_views.signup, name='signup'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('login/', accounts_views.login_view, name='login'),
    path('explore/', include('explore.urls')),
    path('admin/', admin.site.urls),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
