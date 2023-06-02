import requests
import environ
env = environ.Env()
environ.Env.read_env()

prod = bool(env('PROD'))

url = 'http://89.46.34.208/api/notification/check/'


if prod:
    url = 'https://bepro.kz/api/notification/check/'

resp = requests.get(url)
