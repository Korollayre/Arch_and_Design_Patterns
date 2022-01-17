from quopri import decodestring
from requests import GetRequests, PostRequests


class PageNotFound404Error:
    """
    Класс-исключение, обрабатывающий ошибки вызова несуществующей страницы.
    """

    def __call__(self, *args, **kwargs):
        return '404 Error', '404 Error - Page not found'


class Framework:
    """
    Класс — основная логика работы фреймворка
    """

    def __init__(self, urls, middlewares):
        self.urls_lst = urls
        self.middlewares_lst = middlewares

    def __call__(self, environ, start_response):
        url_path = environ['PATH_INFO']

        if not url_path.endswith('/'):
            url_path = f'{url_path}/'

        request = {}
        method = environ['REQUEST_METHOD']
        request['method'] = method

        if method == 'GET':
            request_params = GetRequests().get_request_params(environ)
            request['request_params'] = Framework.decode_value(request_params)
            print(f'Нам пришли GET-параметры: {request["request_params"]}')
        if method == 'POST':
            data = PostRequests().get_request_data(environ)
            request['data'] = Framework.decode_value(data)
            print(f'Нам пришёл post-запрос: {request["data"]}')

        if url_path in self.urls_lst:
            view = self.urls_lst[url_path]
        else:
            view = PageNotFound404Error()

        for middleware in self.middlewares_lst:
            middleware(request)

        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

    @staticmethod
    def decode_value(data) -> dict:
        """
        Функция, декодирующая полученный словарь в utf-8 кодировку.

        :param data: словарь с параметрами url-запроса.
        :return: словарь с параметрами в utf-8 кодировке.
        """
        new_data = {}
        for k, v in data.items():
            if type(v) == str:
                val = bytes(v.replace('%', '=').replace("+", " "), 'utf-8')
                val_decode_str = decodestring(val).decode('utf-8')
                new_data[k] = val_decode_str
            else:
                for el in v:
                    idx = v.index(el)
                    val = bytes(el.replace('%', '=').replace("+", " "), 'utf-8')
                    val_decode_str = decodestring(val).decode('utf-8')
                    v[idx] = val_decode_str
                new_data[k] = v
        return new_data
