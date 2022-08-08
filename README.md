### Prerequisites
- python 3.10
- poetry

Create .env file in config directory and add following values:
```dotenv
DEBUG=
DEBUG_STATIC=
ALLOWED_HOSTS=
MEDIA_PATH=
STATIC_PATH=

POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

CORS_ALLOWED_ORIGIN_REGEXES=
CSRF_TRUSTED_ORIGINS=
CORS_ALLOW_ALL_ORIGINS=
CURRENT_SITE=

EMAIL_HOST=''
EMAIL_PORT=''
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
```

1. poetry shell
2. poetry install
3. python manage.py migrate
4. бэкграунд селери: nohup celery -A auth_user worker -l info &
5. обычный запуск селери: celery -A auth_user worker -l info


https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04-ru

# Deploy:
1. apt update && sudo apt upgrade -y
2. apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
3. apt install software-properties-common -y
4. add-apt-repository ppa:deadsnakes/ppa
5. apt install python3.10
6. curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3.10 -
7. cd /var/www/
8. git clone git@github.com:elefantoteam/BePro-back.git
9. mv BePro-back back
10. cd back
11. poetry shell
12. apt install python3.10-distutils
13. poetry install
14. vim config/.env --заполнить файл переменными
15. sudo -u postgres psql
16. CREATE DATABASE bepro;
17. CREATE USER root WITH PASSWORD 'root';
18. ALTER ROLE root SET client_encoding TO 'utf8';
    ALTER ROLE root SET default_transaction_isolation TO 'read committed';
    ALTER ROLE root SET timezone TO 'UTC';
19. GRANT ALL PRIVILEGES ON DATABASE bepro TO root;
20. \q
21. ./manage.pt migrate
22. ./manage.py createsuperuser
23. ./manage.py collectstatic
24. ufw allow 8000
25. ./manage.py runserver 0.0.0.0:8000
26. ctrl+c
26. sudo nano /etc/systemd/system/gunicorn.socket
    [Unit]
    Description=gunicorn socket

    [Socket]
    ListenStream=/run/gunicorn.sock
    
    [Install]
    WantedBy=sockets.target
27. sudo nano /etc/systemd/system/gunicorn.service
    [Unit]
    Description=gunicorn daemon
    Requires=gunicorn.socket
    After=network.target

    [Service]
    User=root
    Group=www-data
    WorkingDirectory=/var/www/back
    ExecStart=/var/www/back/.venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    config.wsgi:application

    [Install]
    WantedBy=multi-user.target
28. sudo systemctl start gunicorn.socket
    sudo systemctl enable gunicorn.socket
29. file /run/gunicorn.sock
30. nano /etc/nginx/sites-available/default
    server {
        location /django-admin {
                include proxy_params;
                proxy_pass http://unix:/run/gunicorn.sock;
        }
        location /swagger {
                include proxy_params;
                proxy_pass http://unix:/run/gunicorn.sock;
        }
        location /static {
                alias /static;
        }
        location /media {
                alias /var/www/back/media;
        }
    }
31. sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled
32. sudo nginx -t
33. sudo systemctl restart nginx
34. sudo ufw delete allow 8000
    sudo ufw allow 'Nginx Full'
35. apt install redis-server



## server refresh:
1. git pull
2. poetry shell
3. manage.py migrate
4. kill `celery_pid`
5. nohup celery -A auth_user worker -B -l info &
6. systemctl restart gunicorn