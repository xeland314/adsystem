# ads/urls.py
from django.urls import path
from . import views
from ads.views.api import AdListAPIView, CarouselListAPIView

# ¡ESTA LÍNEA ES ESENCIAL! Define el espacio de nombres para tu aplicación.
# Debe coincidir con el nombre que usas en {% url 'ads:...' %} en tus plantillas.
app_name = "ads"


urlpatterns = [
    path("display/", views.ad_display, name="ad_display"),
    path("<int:ad_id>/redirect/", views.ad_redirect, name="ad_redirect"),
    path("statistics/", views.ad_statistics, name="ad_statistics"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path(
        "carousel/<int:carousel_id>/display/",
        views.carousel_display,
        name="carousel_display",
    ),
    path("api/ads/", AdListAPIView.as_view(), name="ad_list_api"),
    path("api/carousels/", CarouselListAPIView.as_view(), name="carousel_list_api"),
]
