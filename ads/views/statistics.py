# ads/views.py
import datetime
import json


from django.shortcuts import render
from django.db.models import Count, Q
from django.db.models.functions import TruncHour, TruncDay
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from ads.models import Ad, Click

# --- Funciones Auxiliares para la Vista de Estadísticas ---

def _parse_date_param(request, param_name, date_format='%Y-%m-%d'):
    """
    Intenta parsear un parámetro de fecha de la solicitud GET.
    Muestra un mensaje de error si el formato es inválido.
    Retorna un objeto date o None.
    """
    date_str = request.GET.get(param_name)
    if date_str:
        try:
            return datetime.datetime.strptime(date_str, date_format).date()
        except ValueError:
            messages.error(
                request,
                f"Formato de fecha para '{param_name}' inválido. Use AAAA-MM-DD."
            )
    return None

def _get_clicks_filter_q(start_date, end_date):
    """
    Construye un objeto Q para filtrar los clics por rango de fechas.
    """
    clicks_filter = Q()
    if start_date:
        clicks_filter &= Q(timestamp__date__gte=start_date)
    if end_date:
        # Filtrar hasta el final del día de la fecha de fin
        clicks_filter &= Q(timestamp__date__lte=end_date)
    return clicks_filter

def _get_global_click_stats(clicks_queryset):
    """
    Calcula y retorna las estadísticas globales de clics.
    """
    total_global_clicks = clicks_queryset.count()
    total_unique_global_clicks = clicks_queryset.values("session_id").distinct().count()
    return total_global_clicks, total_unique_global_clicks

def _get_ad_click_stats(clicks_filter_q):
    """
    Calcula y retorna las estadísticas por anuncio.
    """
    ads_with_clicks = Ad.objects.annotate(
        total_clicks_count=Count("clicks", filter=clicks_filter_q),
        unique_clicks_count=Count(
            "clicks__session_id", distinct=True, filter=clicks_filter_q
        ),
    ).order_by("-total_clicks_count")

    ads_clicks_data = [
        {
            "name": ad.name,
            "total": ad.total_clicks_count,
            "unique": ad.unique_clicks_count,
        }
        for ad in ads_with_clicks
        if ad.total_clicks_count > 0
    ]
    # Filtrar también para la tabla de la plantilla
    ads_for_table = [ad for ad in ads_with_clicks if ad.total_clicks_count > 0]
    return ads_clicks_data, ads_for_table

def _get_timeline_click_stats(clicks_queryset, selected_date):
    """
    Prepara los datos para el gráfico de línea de tiempo (por día u hora).
    """
    clicks_timeline_data = []
    is_hourly_view = False
    timeline_title = "Clicks por Día"
    x_axis_label = "Fecha"

    if selected_date:
        is_hourly_view = True
        timeline_title = f"Clicks por Hora para {selected_date.strftime('%Y-%m-%d')}"
        x_axis_label = "Hora del Día"

        hourly_clicks_queryset = (
            clicks_queryset.filter(timestamp__date=selected_date)
            .annotate(hour=TruncHour("timestamp"))
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("hour")
        )

        for item in hourly_clicks_queryset:
            clicks_timeline_data.append(
                {"time": item["hour"].strftime("%H:%M"), "count": item["count"]}
            )
    else:
        daily_clicks_queryset = (
            clicks_queryset.annotate(date=TruncDay("timestamp"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        for item in daily_clicks_queryset:
            clicks_timeline_data.append(
                {"time": item["date"].strftime("%Y-%m-%d"), "count": item["count"]}
            )

    return clicks_timeline_data, is_hourly_view, timeline_title, x_axis_label

@login_required
def ad_statistics(request):
    """
    Vista para mostrar estadísticas generales de los anuncios con filtrado por fecha.
    """
    # 1. Parsear parámetros de fecha
    start_date = _parse_date_param(request, 'start_date')
    end_date = _parse_date_param(request, 'end_date')
    selected_date = _parse_date_param(request, 'selected_date')

    # 2. Construir filtro base para clics
    clicks_filter_q = _get_clicks_filter_q(start_date, end_date)
    clicks_queryset = Click.objects.filter(clicks_filter_q)

    # 3. Obtener estadísticas globales
    total_global_clicks, total_unique_global_clicks = _get_global_click_stats(clicks_queryset)

    # 4. Obtener estadísticas por anuncio
    ads_clicks_data, ads_for_table = _get_ad_click_stats(clicks_filter_q)

    # 5. Obtener datos para el gráfico de línea de tiempo
    clicks_timeline_data, is_hourly_view, timeline_title, x_axis_label = \
        _get_timeline_click_stats(clicks_queryset, selected_date)

    # 6. Preparar el contexto para la plantilla
    context = {
        "ads_with_clicks": ads_for_table,
        "total_global_clicks": total_global_clicks,
        "total_unique_global_clicks": total_unique_global_clicks,
        "ads_clicks_data_json": json.dumps(ads_clicks_data),
        "clicks_timeline_data_json": json.dumps(clicks_timeline_data),
        "start_date_str": start_date.isoformat() if start_date else '',
        "end_date_str": end_date.isoformat() if end_date else '',
        "selected_date_str": selected_date.isoformat() if selected_date else '',
        "is_hourly_view": is_hourly_view,
        "timeline_title": timeline_title,
        "x_axis_label": x_axis_label,
    }
    return render(request, "ads/ad_statistics.html", context)
