import os
import uuid
from django.db import models
from django.utils import timezone


# Función personalizada para renombrar la imagen con un UUID4
def ad_image_upload_path(instance, filename):
    """
    Renombra el archivo de imagen subido a un nombre UUID4
    manteniendo la extensión original.
    """
    # instance es la instancia del modelo Ad (o el modelo que está siendo guardado)
    # filename es el nombre original del archivo subido (ej. 'mi_banner.png')

    # Obtener la extensión del archivo original
    # os.path.splitext() divide la ruta en (root, ext)
    _, ext = os.path.splitext(filename)

    # Generar un nombre de archivo único usando UUID4
    # uuid.uuid4() genera un UUID aleatorio
    # .hex lo convierte a una cadena hexadecimal
    new_filename = f"{uuid.uuid4().hex}{ext}"

    # Construir la ruta de subida.
    # Aquí puedes añadir directorios si quieres organizar tus imágenes.
    # Por ejemplo, puedes ponerlas en un subdirectorio 'banners/':
    return os.path.join("images", "banners", new_filename)
    # O si solo quieres un directorio 'images' como antes, simplemente:
    # return os.path.join('images', new_filename)


class Campaign(models.Model):
    """
    Modelo para campañas publicitarias.
    """
    name = models.CharField(max_length=200, verbose_name="Nombre de la Campaña")
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    budget = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Presupuesto"
    )
    target_audience = models.TextField(
        blank=True, verbose_name="Audiencia Objetivo"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Última Actualización"
    )

    def save(self, *args, **kwargs):
        """
        Sobrescribimos el método save para asegurarnos de que la fecha de fin
        sea siempre posterior a la fecha de inicio.
        """
        if self.end_date < self.start_date:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio.")
        updated_at = timezone.now()
        if not self.updated_at or self.updated_at < updated_at:
            self.updated_at = updated_at
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = "Campaña"
        ordering = ["-start_date"]


class Keyword(models.Model):
    """
    Modelo para palabras clave que se pueden asociar con anuncios.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Palabra Clave")

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name = "Palabra Clave"
        ordering = ["name"]


class Ad(models.Model):
    """
    Modelo para representar un anuncio publicitario.
    """

    class Gender(models.TextChoices):
        MALE = 'M', "Masculino"
        FEMALE = 'F', "Femenino"
        ANY = 'A', "Cualquiera"

    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="ads", verbose_name="Campaña"
    )
    name = models.CharField(max_length=200, verbose_name="Nombre del Anuncio")
    # ¡Modificamos el argumento upload_to para usar nuestra función!
    image = models.ImageField(
        upload_to=ad_image_upload_path, verbose_name="Imagen del Anuncio"
    )
    target_url = models.URLField(verbose_name="URL de Destino")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Última Actualización"
    )
    # Campo para almacenar el número total de clics. Se actualizará en la vista.
    total_clicks = models.PositiveIntegerField(
        default=0, verbose_name="Total de Clicks"
    )

    # Campos de segmentación
    target_age_min = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Edad Mínima del Público"
    )
    target_age_max = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Edad Máxima del Público"
    )
    target_gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        default=Gender.ANY,
        verbose_name="Género del Público"
    )
    target_location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Ubicación del Público",
        help_text="Lista de ubicaciones separadas por comas (ej. España, México, Colombia)"
    )
    target_keywords = models.ManyToManyField(
        Keyword,
        blank=True,
        verbose_name="Palabras Clave del Público",
        help_text="Selecciona palabras clave que describan a tu audiencia."
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Anuncio"
        ordering = ["-created_at"]


class Click(models.Model):
    """
    Modelo para registrar cada click en un anuncio.
    """

    ad = models.ForeignKey(
        Ad, on_delete=models.CASCADE, related_name="clicks", verbose_name="Anuncio"
    )
    timestamp = models.DateTimeField(
        default=timezone.now, verbose_name="Fecha/Hora del Click"
    )
    user_ip = models.GenericIPAddressField(
        verbose_name="Dirección IP del Usuario", null=True, blank=True
    )
    user_agent = models.TextField(
        verbose_name="User Agent del Navegador", null=True, blank=True
    )
    session_id = models.CharField(
        max_length=255, verbose_name="ID de Sesión (hash)", null=True, blank=True
    )

    def __str__(self):
        return f"Click en {self.ad.name} el {self.timestamp}"

    class Meta:
        verbose_name = "Click"
        ordering = ["-timestamp"]


class Carousel(models.Model):
    """
    Modelo para un carrusel de anuncios, que contiene múltiples Ads.
    """
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="carousels", verbose_name="Campaña"
    )
    name = models.CharField(max_length=200, unique=True, verbose_name="Nombre del Carrusel")
    # Los anuncios en este carrusel. Un carrusel puede tener muchos anuncios,
    # y un anuncio puede estar en muchos carruseles.
    ads = models.ManyToManyField(
        Ad,
        related_name='carousels',
        verbose_name="Anuncios en el Carrusel",
        blank=True # Un carrusel puede crearse sin anuncios al principio
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Carrusel de Anuncios"
        verbose_name_plural = "Carruseles de Anuncios"
        ordering = ['name']
