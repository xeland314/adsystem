# AdSystem

Este proyecto es una aplicación robusta desarrollada con **Django** para la gestión avanzada de anuncios publicitarios, ofreciendo funcionalidades de segmentación, programación, analíticas detalladas y una API REST para integración externa.

## Características Principales

*   **Gestión de Anuncios y Carruseles:** Creación, edición y eliminación de anuncios individuales y carruseles de anuncios.
*   **Autenticación Segura:** Implementación de `django-axes` para una autenticación de usuario más robusta, incluyendo protección contra ataques de fuerza bruta.
*   **Segmentación y Orientación de Anuncios:**
    *   Dirige anuncios a audiencias específicas por **demografía** (edad, género).
    *   Segmentación por **ubicación** geográfica.
    *   Orientación basada en **palabras clave** para intereses y comportamientos.
*   **Gestión de Campañas Mejorada:**
    *   Modelo `Campaign` dedicado para organizar anuncios y carruseles.
    *   Campos como fecha de inicio, fecha de fin, presupuesto y audiencia objetivo.
    *   Filtrado de anuncios y carruseles por campañas activas.
*   **Programación de Anuncios:**
    *   Define horarios específicos (hora de inicio y fin) para la visualización de anuncios.
    *   Permite seleccionar días de la semana para la entrega de anuncios.
*   **Analíticas Avanzadas:**
    *   **Tasa de Clics (CTR):** Seguimiento de impresiones y clics para calcular el CTR.
    *   **Seguimiento de Conversiones:** Registro de diferentes tipos de conversiones atribuidas a los anuncios.
    *   **Pruebas A/B:** Soporte para asignar anuncios a grupos de prueba A/B para evaluar el rendimiento de diferentes creatividades o estrategias.
    *   **Datos Históricos:** Visualización del rendimiento histórico de clics, impresiones y conversiones a lo largo del tiempo.
*   **API RESTful:**
    *   API externa construida con `Django REST Framework` para la entrega programática de anuncios.
    *   Permite a aplicaciones externas solicitar anuncios segmentados y programados.
*   **Documentación de API:** Integración con `drf-yasg` para generar automáticamente documentación interactiva (Swagger UI y ReDoc) de la API.
*   **SDK Minimalista para Web:** Un SDK básico (`sdk/` folder) para facilitar la integración de anuncios en cualquier página web externa, incluyendo un ejemplo de uso con HTML, JavaScript y Tailwind CSS.

## Requisitos

*   Python 3.x
*   Django
*   Django REST Framework
*   drf-yasg
*   django-axes
*   Node.js y npm (para el SDK)

## Instalación

1.  Clona este repositorio:
    ```bash
    git clone https://github.com/your-repo/AdSystem.git
    cd AdSystem
    ```
2.  Crea y activa un entorno virtual (recomendado):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  Instala las dependencias de Python (usando `uv` si está disponible, o `pip`):
    ```bash
    # Si tienes uv instalado (recomendado para pyproject.toml)
    uv sync

    # O si usas pip
    pip install -r pyproject.txt # (assuming you generate this from pyproject.toml)
    # or manually install:
    # pip install django djangorestframework drf-yasg django-axes
    ```
    *Note: `pyproject.toml` and `uv.lock` suggest `uv` is the intended package manager. If `uv` is not installed, you might need to install it first (`pip install uv`) or use `pip` directly.* 

4.  Realiza las migraciones de la base de datos:
    ```bash
    python3 manage.py migrate
    ```
5.  Crea un superusuario para acceder al panel de administración:
    ```bash
    python3 manage.py createsuperuser
    ```
6.  Inicia el servidor de desarrollo de Django:
    ```bash
    python3 manage.py runserver
    ```

## Uso

### Panel de Administración

Accede al panel de administración de Django en `http://127.0.0.1:8000/admin/` para gestionar anuncios, campañas, palabras clave y ver estadísticas.

### API REST

La API REST está disponible en `http://127.0.0.1:8000/ads/api/`.

*   **Endpoint de Anuncios:** `http://127.0.0.1:8000/ads/api/ads/`
    *   Soporta parámetros de consulta para segmentación (ej. `?age=30&gender=M&location=Spain&keywords=tech&ab_test_group=Control`).
*   **Endpoint de Carruseles:** `http://127.0.0.1:8000/ads/api/carousels/`

### Documentación de la API

Puedes acceder a la documentación interactiva de la API en:

*   **Swagger UI:** `http://127.0.0.1:8000/swagger/`
*   **ReDoc:** `http://127.0.0.1:8000/redoc/`

### SDK Minimalista

Para usar el SDK en una página web externa:

1.  Navega al directorio `sdk`:
    ```bash
    cd sdk
    ```
2.  Instala las dependencias de Node.js:
    ```bash
    npm install
    ```
3.  Compila el CSS de Tailwind (necesario para los estilos del SDK):
    ```bash
    npm run build:css
    ```
4.  Abre el archivo `index.html` en tu navegador:
    ```bash
    # Puedes abrirlo directamente o usar una extensión como Live Server en VS Code
    # para servirlo localmente (ej. http://127.0.0.1:5500/index.html)
    ```
    El `index.html` contiene ejemplos de cómo integrar anuncios individuales y carruseles usando el SDK, y también un iframe con el panel de administración de Django.

---
**Nota de Seguridad para Desarrollo:**
Para permitir que el panel de administración de Django se incruste en un `iframe` (como en el ejemplo del SDK), la configuración `X-Frame-Options` ha sido modificada en `AdSystem/settings.py`. En un entorno de producción, se recomienda encarecidamente configurar `X_FRAME_OPTIONS = 'ALLOWFROM'` y especificar dominios de confianza en `CSRF_TRUSTED_ORIGINS` para mitigar riesgos de seguridad como el clickjacking.