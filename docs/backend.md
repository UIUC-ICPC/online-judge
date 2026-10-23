# Backend Development

## Build & Setup 

The project uses `uv` to install and manage Python dependencies.

Install/sync dependencies 
```
uv sync
```

Generate a random secret key
```
uv run python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Ensure your `.env` file is properly set up with the following information:
```
DJANGO_ENV=development
DJANGO_SECRET_KEY=put-generated-key-here
MYSQL_DATABASE=online_judge
MYSQL_USER=someuser
MYSQL_PASSWORD="somepassword"
MYSQL_HOST=put.hostname.here
MYSQL_PORT=somenumber
```

Run: 
```
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Django should start up a server at `http://127.0.0.1:8000/`