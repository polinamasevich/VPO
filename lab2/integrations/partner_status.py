"""Учебное дополнение: проверка доступности сайта существующего Partner.

Не подключено к страницам сайта; предназначено для задания об HTTP-интеграциях.
"""
from urllib.parse import urlsplit
import requests


def check_partner_website(partner):
    url = partner.website
    if urlsplit(url).scheme not in ('http', 'https'):
        raise ValueError('Сайт партнёра должен использовать HTTP или HTTPS')
    try:
        response = requests.get(url, timeout=3, allow_redirects=False)
        return response.status_code == 200
    except requests.RequestException:
        return False
