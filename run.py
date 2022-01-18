from wsgiref.simple_server import make_server

from roach_framework.main import Framework
from urls import FRONTS
from views import ROUTES

APP = Framework(ROUTES, FRONTS)

with make_server('', 8000, APP) as server:
    print(f'Server running on http://localhost:{server.server_port}...')
    server.serve_forever()
