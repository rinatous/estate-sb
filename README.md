### estate-sb

Install dependencies

```
./install_webapp.sh
```

Configure PostgreSQL connection in settings.py

```python
settings = {
    'database': {
        'host': '127.0.0.1',
        'port': 5432,
        'user': 'postgres',
        'password': 'secret',
        'database': 'database_name'
    }
}
```

Tables will be created automatically on startup

Debug mode
```
$ cd webapp
$ python3 run.py
```

Production mode
```
$ cd webapp
$ python3 -O run.py
```

Tests
```
$ cd tests
$ pytest -v test_queue.py
```
