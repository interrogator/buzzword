from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = (
    [
        path("", include("start.urls")),
        path("", include("accounts.urls")),
        path("accounts/", include("accounts.urls")),
        path("read/", include("read.urls")),
        path("compare/", include("compare.urls")),
        path("explore/", include("explore.urls")),
        path("example/", include("example.urls")),
        path("martor/", include("martor.urls")),
        path("admin/login/", admin.site.urls),
        path("resources/", include("django_plotly_dash.urls")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL)
)

