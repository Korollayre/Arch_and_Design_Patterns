from wsgiref.simple_server import make_server

from roach_framework.main import Framework
from urls import routes, fronts

app = Framework(routes, fronts)

with make_server('', 8000, app) as server:
    print(f'Server running on http://localhost:{server.server_port}...')
    server.serve_forever()
