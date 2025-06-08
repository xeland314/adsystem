# ads/admin.py
from django.contrib import admin
from django.db.models import Count  # Para agregar anotaciones de conteo
from ads.models import Ad, Click


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """
    Configuración de la administración para el modelo Ad.
    """

    list_display = (
        "name",
        "image_tag",
        "target_url",
        "is_active",
        "total_clicks",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "target_url")
    readonly_fields = ("created_at", "updated_at", "total_clicks")
    fieldsets = (
        (None, {"fields": ("name", "image", "target_url", "is_active")}),
        (
            "Información Adicional",
            {
                "fields": ("total_clicks", "created_at", "updated_at"),
                "classes": (
                    "collapse",
                ),  # Opcional: para que se pueda plegar en el admin
            },
        ),
    )

    def image_tag(self, obj):
        """
        Muestra la imagen del anuncio en el listado del admin.
        """
        if obj.image:
            from django.utils.html import mark_safe

            return mark_safe(
                f'<img src="{obj.image.url}" style="width: 100px; height: auto;" />'
            )
        return "No Image"

    image_tag.short_description = "Imagen"

    def get_queryset(self, request):
        """
        Optimiza el queryset para incluir el conteo de clics.
        """
        queryset = super().get_queryset(request)
        # Anotar el queryset con el conteo de clics para cada anuncio
        return queryset.annotate(click_count=Count("clicks"))

    def total_clicks(self, obj):
        """
        Muestra el conteo de clics para cada anuncio en el listado.
        """
        # Se obtiene el conteo de la anotación 'click_count'
        return obj.click_count

    total_clicks.admin_order_field = "click_count"  # Permite ordenar por este campo
    total_clicks.short_description = "Total de Clicks"


@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    """
    Configuración de la administración para el modelo Click.
    """

    list_display = ("ad_name", "timestamp", "user_ip", "user_agent_short")
    list_filter = ("ad", "timestamp")
    search_fields = ("ad__name", "user_ip", "user_agent")
    readonly_fields = (
        "ad",
        "timestamp",
        "user_ip",
        "user_agent",
        "session_id",
    )  # Todos los campos son de solo lectura

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
