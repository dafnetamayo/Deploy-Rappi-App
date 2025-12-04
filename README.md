# RAPPITESO

Proyecto de ejemplo para un sistema de pedidos desarrollado con Django.

## Resumen

RAPPITESO es una aplicación web basada en Django que gestiona pedidos y restaurantes (app `orders`).
El proyecto incluye configuración para ejecución local con SQLite y contenedores mediante Docker/Docker Compose.

## Stack

- Python 3.x
- Django
- Docker / docker-compose (opcional)

## Estructura principal

- `manage.py` - script de gestión de Django
- `web_project/` - configuración del proyecto (settings, urls, wsgi, asgi)
- `orders/` - aplicación principal con modelos, vistas, serializers y tests
- `requirements.txt` - dependencias Python
- `Dockerfile`, `docker-compose.yml` - para ejecución en contenedor

## Requisitos previos

- Python 3.8+ instalado
- pip
- (Opcional) Docker y Docker Compose

## Instalación y ejecución local (entorno virtual recomendado)

1. Clonar el repositorio:

```bash
git clone <url-del-repo>
cd RAPPITESO
```

2. Crea y activa un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Aplica migraciones y crea un superusuario (opcional):

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Ejecuta el servidor de desarrollo:

```bash
python manage.py runserver
```

Abre http://127.0.0.1:8000/ en tu navegador.

## Uso con Docker (opcional)

Si prefieres usar Docker, construye y levanta los servicios con Docker Compose:

```bash
docker compose up --build
```

Esto ejecutará la aplicación dentro de un contenedor. Revisa `docker-compose.yml` para los detalles de puertos y servicios.

## Ejecutar tests

Para correr la suite de tests (ejemplo: app `orders`):

```bash
python manage.py test
```