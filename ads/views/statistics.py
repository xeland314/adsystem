# ads/views.py
import datetime
import json

from django.shortcuts import render
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncHour, TruncDay
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from ads.models import Ad, Click, Conversion

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
    Calcula y retorna las estadísticas por anuncio, incluyendo CTR.
    """
    ads_with_stats = Ad.objects.annotate(
        total_clicks_count=Count("clicks", filter=clicks_filter_q),
        unique_clicks_count=Count(
            "clicks__session_id", distinct=True, filter=clicks_filter_q
        ),
    ).order_by("-total_clicks_count")

    ads_clicks_data = []
    ads_for_table = []

    for ad in ads_with_stats:
        ctr = 0.0
        if ad.total_impressions > 0:
            ctr = (ad.total_clicks_count / ad.total_impressions) * 100

        if ad.total_clicks_count > 0 or ad.total_impressions > 0:
            ads_clicks_data.append(
                {
                    "name": ad.name,
                    "total": ad.total_clicks_count,
                    "unique": ad.unique_clicks_count,
                    "impressions": ad.total_impressions,
                    "ctr": round(ctr, 2),
                }
            )
            # También para la tabla de la plantilla
            ad.ctr = round(ctr, 2)
            ads_for_table.append(ad)

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

def _get_historical_impressions_stats(start_date, end_date):
    """
    Calcula las impresiones históricas por día.
    """
    impressions_queryset = Ad.objects.filter(total_impressions__gt=0)
    if start_date:
        impressions_queryset = impressions_queryset.filter(updated_at__date__gte=start_date)
    if end_date:
        impressions_queryset = impressions_queryset.filter(updated_at__date__lte=end_date)

    daily_impressions = impressions_queryset.annotate(date=TruncDay('updated_at')) \
                                            .values('date') \
                                            .annotate(total_impressions=Sum('total_impressions')) \
                                            .order_by('date')
    return [{'date': item['date'].strftime('%Y-%m-%d'), 'count': item['total_impressions']} for item in daily_impressions]

def _get_historical_conversions_stats(start_date, end_date):
    """
    Calcula las conversiones históricas por día y tipo.
    """
    conversions_queryset = Conversion.objects.all()
    if start_date:
        conversions_queryset = conversions_queryset.filter(timestamp__date__gte=start_date)
    if end_date:
        conversions_queryset = conversions_queryset.filter(timestamp__date__lte=end_date)

    daily_conversions = conversions_queryset.annotate(date=TruncDay('timestamp')) \
                                            .values('date', 'conversion_type') \
                                            .annotate(count=Count('id')) \
                                            .order_by('date', 'conversion_type')

    # Reestructurar para Plotly: un diccionario por tipo de conversión
    conversions_by_type = {}
    for item in daily_conversions:
        date_str = item['date'].strftime('%Y-%m-%d')
        conv_type = item['conversion_type']
        count = item['count']
        if conv_type not in conversions_by_type:
            conversions_by_type[conv_type] = {'dates': [], 'counts': []}
        conversions_by_type[conv_type]['dates'].append(date_str)
        conversions_by_type[conv_type]['counts'].append(count)

    return conversions_by_type

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

    # 5. Obtener datos para el gráfico de línea de tiempo de clics
    clicks_timeline_data, is_hourly_view, timeline_title, x_axis_label = \
        _get_timeline_click_stats(clicks_queryset, selected_date)

    # 6. Obtener datos históricos de impresiones y conversiones
    historical_impressions_data = _get_historical_impressions_stats(start_date, end_date)
    historical_conversions_data = _get_historical_conversions_stats(start_date, end_date)

    # 7. Preparar el contexto para la plantilla
    context = {
        "ads_with_clicks": ads_for_table,
        "total_global_clicks": total_global_clicks,
        "total_unique_global_clicks": total_unique_global_clicks,
        "ads_clicks_data_json": json.dumps(ads_clicks_data),
        "clicks_timeline_data_json": json.dumps(clicks_timeline_data),
        "historical_impressions_data_json": json.dumps(historical_impressions_data),
        "historical_conversions_data_json": json.dumps(historical_conversions_data),
        "start_date_str": start_date.isoformat() if start_date else '',
        "end_date_str": end_date.isoformat() if end_date else '',
        "selected_date_str": selected_date.isoformat() if selected_date else '',
        "is_hourly_view": is_hourly_view,
        "timeline_title": timeline_title,
        "x_axis_label": x_axis_label,
    }
    return render(request, "ads/ad_statistics.html", context)
