from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include("start.urls")),
    path('', include("accounts.urls")),
    path('explore/', include('explore.urls')),
    path('admin/', admin.site.urls),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
