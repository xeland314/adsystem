# ads/admin.py
from django.contrib import admin
from .models import Ad, Click, Carousel, Keyword, Campaign
from django.db.models import Count


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """
    Configuración de la administración para el modelo Campaign.
    """
    list_display = (
        "name",
        "start_date",
        "end_date",
        "budget",
        "is_active",
    )
    list_filter = ("is_active", "start_date", "end_date")
    search_fields = ("name", "target_audience")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """
    Configuración de la administración para el modelo Ad.
    """

    list_display = (
        "name",
        "campaign",
        "image_tag",
        "target_url",
        "is_active",
        "total_clicks",
        "created_at",
        "display_start_time",
        "display_end_time",
        "display_days_of_week",
    )
    list_filter = ("is_active", "created_at", "target_gender", "campaign", "display_days_of_week")
    search_fields = ("name", "target_url", "target_location")
    readonly_fields = ("created_at", "updated_at", "total_clicks")
    fieldsets = (
        (None, {"fields": ("campaign", "name", "image", "target_url", "is_active")}),
        (
            "Segmentación de Audiencia",
            {
                "fields": (
                    "target_age_min",
                    "target_age_max",
                    "target_gender",
                    "target_location",
                    "target_keywords",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Programación de Anuncios",
            {
                "fields": (
                    "display_start_time",
                    "display_end_time",
                    "display_days_of_week",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Información Adicional",
            {
                "fields": ("total_clicks", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
    filter_horizontal = ("target_keywords",)

    def image_tag(self, obj):
        """
        Muestra la imagen del anuncio en el listado del admin.
        """
        if obj.image:
            from django.utils.html import mark_safe

            return mark_safe(
                f'<img src="{obj.image.url}" style="width: 100px; height: auto; border-radius: 8px;" />'
            )
        return "No Image"

    image_tag.short_description = "Imagen"

    def get_queryset(self, request):
        """
        Optimiza el queryset para incluir el conteo de clics.
        """
        queryset = super().get_queryset(request)
        return queryset.annotate(click_count=Count("clicks"))

    def total_clicks(self, obj):
        """
        Muestra el conteo de clics para cada anuncio en el listado.
        """
        return obj.click_count

    total_clicks.admin_order_field = "click_count"
    total_clicks.short_description = "Total de Clicks"


@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    """
    Configuración de la administración para el modelo Click.
    """

    list_display = ("ad_name", "timestamp", "user_ip", "user_agent_short")
    list_filter = ("ad", "timestamp")
    search_fields = ("ad__name", "user_ip", "user_agent")
    readonly_fields = ("ad", "timestamp", "user_ip", "user_agent", "session_id")

    def ad_name(self, obj):
        """
        Muestra el nombre del anuncio al que pertenece el click.
        """
        return obj.ad.name

    ad_name.short_description = "Anuncio"
    ad_name.admin_order_field = "ad__name"

    def user_agent_short(self, obj):
        """
        Muestra una versión abreviada del user agent.
        """
        return (
            obj.user_agent[:100] + "..."
            if obj.user_agent and len(obj.user_agent) > 100
            else obj.user_agent
        )

    user_agent_short.short_description = "User Agent (Resumen)"


@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    """
    Configuración de la administración para el modelo Carousel.
    """

    list_display = ("name", "campaign", "is_active", "ad_count", "created_at", "updated_at")
    list_filter = ("is_active", "campaign")
    search_fields = ("name",)
    filter_horizontal = (
        "ads",
    )  # Para un mejor selector del ManyToManyField en el admin
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("campaign", "name", "ads", "is_active")}),
        (
            "Información Adicional",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def ad_count(self, obj):
        """
        Muestra el número de anuncios en el carrusel.
        """
        return obj.ads.count()

    ad_count.short_description = "Número de Anuncios"


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    """
    Configuración de la administración para el modelo Keyword.
    """

    list_display = ("name",)
    search_fields = ("name",)
