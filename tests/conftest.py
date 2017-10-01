# coding=utf-8

import pytest
import yaml


settings = yaml.load(open('config.yaml', 'r').read())


@pytest.fixture
def configs():
    class Configs:
        host = settings['host']
        port = settings['port']

        def url(self, uri):
            return 'http://{0}:{1}{2}'.format(self.host, self.port, uri)

    return Configs()
