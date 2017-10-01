# coding=utf-8

from functools import partial
from sanic import Sanic
from asyncpg import create_pool

from apps import PagesHandler, PageHandler, IndexHandler, QueueHandler
from crawler import crawler_executor
from settings import settings


app = Sanic()
app.add_task(crawler_executor(app))

route = partial(app.route, methods=frozenset(['GET', 'POST', 'PATCH', 'DELETE']))
run = partial(app.run, host='0.0.0.0', port=8088)


@app.listener('before_server_start')
async def register_db(app, loop):
    app.pg_pool = await create_pool(**settings['database'], loop=loop, max_size=10)
    # check if tables exists
    async with app.pg_pool.acquire() as conn:
        res = await conn.fetchrow("SELECT COUNT(*) as count FROM pg_catalog.pg_tables WHERE tablename LIKE 'estate%'")
        if res['count'] == 0:
            await conn.execute(
                'CREATE TABLE estate_pages ('
                'id bigserial, '
                'title character varying(2048), '
                'description character varying(4096), '
                'url character varying(2048), '
                'images character varying(256)[], '
                'PRIMARY KEY (id), '
                'UNIQUE (url))')
            await conn.execute(
                'CREATE TABLE estate_queue ('
                'page character varying(4096) NOT NULL, '
                'in_progress smallint DEFAULT 0, '
                'PRIMARY KEY (page))')
            if __debug__:
                print('Database tables created')


@route('/')
def index(req):
    return IndexHandler(app, req).run()


@route('/queue')
def queue(req):
    return QueueHandler(app, req).run()


@route('/pages/<page_id:int>')
def page(req, page_id):
    return PageHandler(app, req, page_id).run()


@route('/pages')
def pages(req):
    return PagesHandler(app, req).run()


if __debug__:
    print('Run debug')
    run(debug=True)
else:
    run()
