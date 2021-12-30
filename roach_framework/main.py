class PageNotFound404Error:
    """
    Класс - исключение для обработки ошибки вызова несуществующей страницы.
    """

    def __call__(self, *args, **kwargs):
        return '404 Error', '404 Error - Page not found'


class Framework:
    """
    Класс - основная логика работы фреймворка
    """
    def __init__(self, urls, middlewares):
        self.urls_lst = urls
        self.middlewares_lst = middlewares

    def __call__(self, environ, start_response):
        url_path = environ['PATH_INFO']

        if not url_path.endswith('/'):
            url_path = f'{url_path}/'

        if url_path in self.urls_lst:
            view = self.urls_lst[url_path]
        else:
            view = PageNotFound404Error()

        request = {}

        for middleware in self.middlewares_lst:
            middleware(request)

        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]
