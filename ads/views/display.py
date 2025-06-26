import datetime
import hashlib
import uuid

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q

from ads.models import Ad, Click, Campaign


def get_client_ip(request):
    """
    Obtiene la dirección IP del cliente desde la solicitud.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_user_agent(request):
    """
    Obtiene el User Agent del cliente desde la solicitud.
    """
    return request.META.get("HTTP_USER_AGENT", "")


def ad_display(request):
    """
    Vista para mostrar un anuncio basado en la segmentación y campañas activas.
    """
    # Obtener el contexto del usuario
    user_age = request.GET.get('age')
    user_gender = request.GET.get('gender')
    user_location = request.GET.get('location')
    page_keywords = request.GET.getlist('keywords')

    # Filtrar anuncios activos y de campañas activas
    today = timezone.now().date()
    ads = Ad.objects.filter(
        is_active=True,
        campaign__is_active=True,
        campaign__start_date__lte=today,
        campaign__end_date__gte=today
    )

    # Filtrar por edad
    if user_age:
        ads = ads.filter(
            Q(target_age_min__lte=user_age) | Q(target_age_min__isnull=True),
            Q(target_age_max__gte=user_age) | Q(target_age_max__isnull=True),
        )

    # Filtrar por género
    if user_gender:
        ads = ads.filter(Q(target_gender=user_gender) | Q(target_gender='A'))

    # Filtrar por ubicación
    if user_location:
        ads = ads.filter(Q(target_location__icontains=user_location) | Q(target_location__exact=''))

    # Filtrar por palabras clave
    if page_keywords:
        ads = ads.filter(Q(target_keywords__name__in=page_keywords) | Q(target_keywords__isnull=True)).distinct()

    # Seleccionar un anuncio al azar de los filtrados
    ad = ads.order_by('?').first()

    # Fallback a un anuncio general si no se encuentra ninguno
    if not ad:
        ad = Ad.objects.filter(
            is_active=True,
            campaign__is_active=True,
            campaign__start_date__lte=today,
            campaign__end_date__gte=today,
            target_age_min__isnull=True,
            target_age_max__isnull=True,
            target_gender='A',
            target_location__exact='',
            target_keywords__isnull=True
        ).order_by('?').first()

    return render(request, 'ads/ad_display.html', {'ad': ad})


def ad_redirect(request, ad_id):
    """
    Vista para redirigir al usuario a la URL de destino del anuncio
    y registrar el clic de forma más robusta con rate limiting.
    """
    ad = get_object_or_404(Ad, id=ad_id)

    user_ip = get_client_ip(request)
    user_agent = get_user_agent(request)

    # Generar un hash para el session_id (IP + User Agent). Esto ayuda a identificar
    # de manera más única a un "usuario" o "dispositivo" para el rate limiting.
    if user_ip and user_agent:
        session_string = f"{user_ip}-{user_agent}"
    else:
        # Fallback a un UUID si no se puede obtener IP o User Agent (caso raro, bot)
        session_string = str(uuid.uuid4())
    session_hash = hashlib.sha256(session_string.encode()).hexdigest()

    # --- Lógica de prevención de clics repetidos/bots (Rate Limiting) ---
    # Establece un umbral de tiempo (ej. 5 segundos) para considerar un clic como "reciente".
    # Si un click de la misma "sesión" para el mismo anuncio ocurre dentro de este tiempo,
    # no se registrará un nuevo click.
    time_threshold = timezone.now() - datetime.timedelta(seconds=5)  # 5 segundos

    # Busca si ya existe un click reciente para este anuncio y esta sesión
    recent_click = Click.objects.filter(
        ad=ad, session_id=session_hash, timestamp__gte=time_threshold
    ).first()

    # Solo registra el click si no hay uno reciente de la misma sesión
    if not recent_click:
        Click.objects.create(
            ad=ad, user_ip=user_ip, user_agent=user_agent, session_id=session_hash
        )
        # Incrementa el contador total de clics del anuncio solo si el click es "válido"
        ad.total_clicks += 1
        ad.save()
    else:
        # Opcional: Podrías loggear que un clic fue bloqueado por rate limiting
        print(
            f"Click bloqueado por rate limiting para ad_id={ad_id}, session_id={session_hash}"
        )

    # Finalmente, redirige al usuario a la URL de destino del anuncio
    return redirect(ad.target_url)
