from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Q
import datetime

from ads.models import Carousel


def carousel_display(request, carousel_id):
    """
    Vista para mostrar un carrusel de anuncios de campañas activas y programadas.
    """
    today = timezone.now().date()
    now = timezone.now().time()
    current_day_of_week = datetime.datetime.now().strftime('%a').upper() # Ej. MON, TUE

    # Obtener el carrusel y sus anuncios activos relacionados.
    # Usamos .prefetch_related('ads') para cargar los anuncios de una vez y evitar consultas N+1.
    carousel = get_object_or_404(
        Carousel.objects.prefetch_related("ads").filter(
            is_active=True,
            campaign__is_active=True,
            campaign__start_date__lte=today,
            campaign__end_date__gte=today
        ),
        id=carousel_id
    )

    # Filtrar solo los anuncios activos dentro del carrusel
    ads = carousel.ads.filter(is_active=True)

    # Filtrar por horario
    ads = ads.filter(
        Q(display_start_time__lte=now) | Q(display_start_time__isnull=True),
        Q(display_end_time__gte=now) | Q(display_end_time__isnull=True),
    )

    # Filtrar por día de la semana
    ads = ads.filter(
        Q(display_days_of_week__icontains=current_day_of_week) | Q(display_days_of_week__exact='')
    )

    ads = ads.order_by("?")  # Orden aleatorio de los ads

    context = {
        "carousel": carousel,
        "ads": ads,
    }
    return render(request, "ads/ad_carousel.html", context)
