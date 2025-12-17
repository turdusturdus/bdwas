from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler403, handler404, handler500
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]

handler403 = core_views.error_403
handler404 = core_views.error_404
handler500 = core_views.error_500
