from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('movies.api.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(
        path('debug/', include(debug_toolbar.urls))
    )
