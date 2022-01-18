from time import time


class AppRoute:
    """
    Класс-декоратор, основная задача которого -
    заполнения словаря routes связкой url: view.
    """
    def __init__(self, routes: dict, url: str):
        self.routes = routes
        self.url = url

    def __call__(self, cls):
        self.routes[self.url] = cls()


class TimeDeco:
    """
    Класс-декоратор, основная задача которого -
    Вывод в терминал название функции (метода), и время
    её (его) выполнения.
    """
    def __init__(self, name: str):
        self.name = name

    def __call__(self, cls):
        def decorated(*args, **kwargs):
            start_time = time()
            res = cls(*args, **kwargs)
            end_time = time()

            print(f'Debug-----> Время выполнения {self.name} - {end_time - start_time} ms')
            return res

        return decorated
