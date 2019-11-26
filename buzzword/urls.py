from django.contrib import admin
from django.urls import include, path
from explorer import __main__

# from explore.views import explore

urlpatterns = [
    path('', include("start.urls")),
    path('explore/', include('explore.urls')),
    path('admin/', admin.site.urls),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]
