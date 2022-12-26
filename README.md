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

ACCESS_TOKEN_LIFETIME_DAYS=0
ACCESS_TOKEN_LIFETIME_MINUTES=5
REFRESH_TOKEN_LIFETIME_DAYS=90
REFRESH_TOKEN_LIFETIME_MINUTES=0

EMAIL_HOST=''
EMAIL_PORT=''
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD=''
```

1. poetry shell
2. poetry install
3. python manage.py migrate
4. бэкграунд селери: nohup celery -A auth_user worker -B -l info &
5. обычный запуск селери: celery -A auth_user worker -B -l info


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
21. sudo apt-get install libpangocairo-1.0-0
22. ./manage.py migrate
23. ./manage.py createsuperuser
24. ./manage.py collectstatic
25. ufw allow 8000
26. ./manage.py runserver 0.0.0.0:8000
27. ctrl+c
28. sudo nano /etc/systemd/system/gunicorn.socket
    [Unit]
    Description=gunicorn socket

    [Socket]
    ListenStream=/run/gunicorn.sock
    
    [Install]
    WantedBy=sockets.target
29. sudo nano /etc/systemd/system/gunicorn.service
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
30. sudo systemctl start gunicorn.socket
    sudo systemctl enable gunicorn.socket
31. file /run/gunicorn.sock
32. nano /etc/nginx/sites-available/default
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
33. sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled
34. sudo nginx -t
35. sudo systemctl restart nginx
36. sudo ufw delete allow 8000
    sudo ufw allow 'Nginx Full'
37. apt install redis-server
38. cd media
39. mkdir tests_pdf
40. cd tests_pdf
41. mkdir tests_one_heart_pro, tests_two_brain, tests_three_brain_pro, tests_four_heart
42. cd ../
43. mkdir statistics
44. cd statistics
45. mkdir double_stats
46. mkdir general_stats
47. mkdir history_stats
48. mkdir inverted_stats
49. применить все функции на базу данных из папки sql_queries



## server refresh:
1. git pull
2. poetry shell
3. manage.py migrate
4. kill `celery_pid`
5. nohup celery -A auth_user worker -B -l info &
6. systemctl restart gunicorn