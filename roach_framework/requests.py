class GetRequests:

    @staticmethod
    def get_request_params(environ) -> dict:
        """
        Функция, преобразующая строку url-запроса
        в словарь с параметрами этого запроса.

        :param environ: словарь данных от сервера.
        :return: словарь параметров.
        """

        data = environ['QUERY_STRING']

        res = {}
        if data:
            params = data.split('&')
            for item in params:
                key, value = item.split('=')
                res[key] = value
        return res


class PostRequests:
    @staticmethod
    def get_wsgi_input_data(environ) -> bytes:
        """
        Функция, проверяющая наличие данных в post-запросе.

        :param environ: словарь данных от сервера.
        :return: параметры запроса в байтовом виде.
        """
        content_length_data = environ.get('CONTENT_LENGTH')
        content_length = int(content_length_data) if content_length_data else 0

        data = environ['wsgi.input'].read(content_length) \
            if content_length > 0 else b''
        return data

    @staticmethod
    def get_request_data(environ) -> dict:
        """
        Функция, преобразующая байтовую строку в словарь параметров.

        :param environ: словарь данных от сервера.
        :return: словарь параметров.
        """
        res = {}
        data = PostRequests.get_wsgi_input_data(environ)
        if data:
            data_str = data.decode(encoding='utf-8')
            params = data_str.split('&')

            for item in params:
                key, value = item.split('=')
                res[key] = value

        return res
