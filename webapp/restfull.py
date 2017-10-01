# coding=utf-8

from sanic.response import HTTPResponse


class Restfull:
    def __init__(self, app, request):
        self.app = app
        self.request = request

    @classmethod
    def get(cls):
        return HTTPResponse(status=405)

    @classmethod
    def post(cls):
        return HTTPResponse(status=405)

    @classmethod
    def patch(cls):
        return HTTPResponse(status=405)

    @classmethod
    def delete(cls):
        return HTTPResponse(status=405)

    def run(self):
        if self.request.method == 'GET':
            return self.get()
        elif self.request.method == 'POST':
            return self.post()
        elif self.request.method == 'PATCH':
            return self.patch()
        elif self.request.method == 'DELETE':
            return self.delete()

        return HTTPResponse(status=405)
