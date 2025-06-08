# AdSystem

Este proyecto es una aplicación desarrollada con **Django** que permite crear y administrar anuncios (ads). Además, ofrece la visualización de estadísticas de los anuncios utilizando **Plotly.js** para gráficos interactivos.

## Características

- Creación, edición y eliminación de anuncios.
- Administración centralizada de campañas publicitarias.
- Visualización de estadísticas y métricas de anuncios con gráficos interactivos gracias a Plotly.js.

## Requisitos

- Python 3.x
- Django
- plotly

## Instalación

1. Clona este repositorio.
2. Instala las dependencias:
    ```bash
    pip install -r pyproject.toml
    ```
3. Realiza las migraciones:
    ```bash
    python manage.py migrate
    ```
4. Inicia el servidor:
    ```bash
    python manage.py runserver
    ```

## Uso

Accede a la interfaz web para crear y administrar anuncios, y consulta las estadísticas gráficas.
