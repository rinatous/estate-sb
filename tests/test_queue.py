# coding=utf-8

import pytest
import requests


@pytest.mark.parametrize('case', [
    'https://www.google.com/',
    'https://www.yandex.ru/',
    'https://www.rambler.ru/',
    pytest.param('http://whaaaaat', marks=pytest.mark.xfail)
])
def test_single_page(case, configs):
    r = requests.post(
        configs.url('/queue'), json={'page': case})

    assert r.status_code in [200, 201], 'Error message: {0}'.format(r.text)


@pytest.mark.parametrize('case', [
    'https://www.google.com/\nhttps://www.google.ru/',
    'https://www.yandex.ru/\nhttps://mail.yandex.ru/',
    'https://www.avito.ru/\nhttps://www.cian.ru/'
])
def test_multiple_pages(case, configs):
    r = requests.post(
        configs.url('/queue'), json={'pages': case})

    assert r.status_code in [200, 201], 'Error message: {0}'.format(r.text)
