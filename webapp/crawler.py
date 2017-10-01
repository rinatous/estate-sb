# coding=utf-8

import asyncio
import aiohttp
from collections import namedtuple
import lxml.html
import re

WebPage = namedtuple('WebPage', ['title', 'description', 'images'])
cian = re.compile(r'.+cian\.ru.+')
avito = re.compile(r'.+avito\.ru.+')

sql_fetch = '''WITH cve AS (SELECT page FROM estate_queue WHERE in_progress = 0 LIMIT 1)
UPDATE estate_queue q SET in_progress = 1 FROM cve WHERE q.page = cve.page RETURNING q.page'''
sql_delete = '''DELETE FROM estate_queue WHERE page = $1'''
sql_insert = '''INSERT INTO estate_pages (title, description, url, images) VALUES ($1, $2, $3, $4)'''
sql_update = '''UPDATE estate_pages SET title = $1, description = $2, images = $3 WHERE id = $4'''


async def crawler_executor(app):
    # skip start up chaos
    await asyncio.sleep(10)
    while True:
        async with app.pg_pool.acquire() as conn:
            while True:
                res = await conn.fetchrow(sql_fetch)
                if res:
                    if __debug__:
                        print('Fetching', res['page'])

                    wp = await fetch_content(res['page'])
                    if wp.title and wp.description:
                        res2 = await conn.fetchrow('SELECT id FROM estate_pages WHERE url = $1', res['page'])
                        if res2:
                            await conn.execute(sql_update, wp.title, wp.description, wp.images, res2['id'])
                        else:
                            await conn.execute(sql_insert, wp.title, wp.description, res['page'], wp.images)
                    await conn.execute(sql_delete, res['page'])
                else:
                    if __debug__:
                        print('Queue is empty')
                    break
        await asyncio.sleep(60)


async def fetch_content(url):
    t = None
    d = None
    i = []
    is_cian = cian.match(url) is not None
    is_avito = avito.match(url) is not None
    if is_cian or is_avito:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                http_page = await response.text()
                doc = lxml.html.fromstring(http_page)

                for _ in doc.xpath('//meta'):
                    if _.get('property') == 'og:title':
                        t = _.get('content')
                    elif _.get('property') == 'og:description':
                        d = _.get('content')
                if is_cian:
                    for _ in doc.xpath('//div[@class="fotorama"]/img'):
                        i.append(_.get('src'))
                else:
                    for _ in doc.xpath('//div[@class="gallery-img-frame js-gallery-img-frame"]'):
                        i.append(_.get('data-url'))
    return WebPage(t, d, i)
