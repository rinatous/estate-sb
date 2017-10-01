# coding=utf-8

from restfull import Restfull
from sanic.response import json, HTTPResponse
import re


url_regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class IndexHandler(Restfull):
    @classmethod
    def get(cls):
        return json({
            '/': 'This page',
            '/queue': 'Queue management',
            '/pages': 'Pages retrieved from web'
        })


class QueueHandler(Restfull):
    async def post(self):
        urls = []

        one_url = self.request.json.get('page')
        if one_url:
            if not url_regex.match(one_url):
                return HTTPResponse(body='Invalid url', status=501)
            urls.append(one_url)

        many_url = self.request.json.get('pages')
        if many_url:
            if isinstance(many_url, str):
                many_url = many_url.split('\n')
            elif isinstance(many_url, list):
                pass
            else:
                return HTTPResponse(body='Pages type is unsupported', status=501)
            for url in many_url:
                if url_regex.match(url):
                    urls.append(url)

        async with self.app.pg_pool.acquire() as conn:
            for url in urls:
                res = await conn.fetchrow('SELECT * FROM estate_queue WHERE page = $1', url)
                if not res:
                    await conn.execute('INSERT INTO estate_queue (page) VALUES ($1)', url)
        return HTTPResponse(status=201)


class PagesHandler(Restfull):
    possible_order = frozenset(['id', 'title'])

    async def get(self):
        result = {
            'items': 0,
            'data': []
        }
        async with self.app.pg_pool.acquire() as conn:
            page = int(self.request.raw_args.get('page', 1))
            field = self.request.raw_args.get('order', 'id')
            direction = 'DESC' if self.request.raw_args.get('dir', 'down') == 'down' else 'ASC'
            sql = 'SELECT id, title FROM estate_pages ORDER BY {0} {1} LIMIT 100 OFFSET {2}'.format(
                field if field in self.possible_order else 'id',
                direction,
                (page-1)*100)
            if __debug__:
                print('SQL:', sql)
            rows = await conn.fetch(sql)
            result['data'] = [dict(r.items()) for r in rows]
            result['items'] = len(rows)
        return json(result)


class PageHandler(Restfull):
    def __init__(self, a, r, page_id):
        super(PageHandler, self).__init__(a, r)
        self.page_id = page_id

    async def get(self):
        async with self.app.pg_pool.acquire() as conn:
            result = await conn.fetchrow('SELECT * FROM estate_pages WHERE id = $1', self.page_id)
            if result:
                return json({
                    'id': result['id'],
                    'title': result['title'],
                    'description': result['description'],
                    'url': result['url']
                })
            else:
                return HTTPResponse(status=404)

    async def delete(self):
        async with self.app.pg_pool.acquire() as conn:
            result = await conn.fetchrow('SELECT * FROM estate_pages WHERE id = $1', self.page_id)
            if result:
                await conn.execute('DELETE FROM estate_pages WHERE id = $1', self.page_id)
                return HTTPResponse(status=200)
            else:
                return HTTPResponse(status=404)
