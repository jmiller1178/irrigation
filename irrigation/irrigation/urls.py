from django.conf import  settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    url(r'', include('sprinklesmart.urls')),
    url(r'^/', include('sprinklesmart.urls')),
    url(r'^admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
       url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
