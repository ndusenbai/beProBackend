### Prerequisites
- python 3.10
- poetry

Create .env file in config directory and add following values:
```dotenv
DEBUG=
DEBUG_STATIC=
ALLOWED_HOSTS=
CORS_ALLOWED_ORIGIN_REGEXES=
MEDIA_PATH=
STATIC_PATH=

POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

CORS_ALLOWED_ORIGIN_REGEXES=
CSRF_TRUSTED_ORIGINS=
```

1. poetry shell
2. poetry install
3. python manage.py migrate