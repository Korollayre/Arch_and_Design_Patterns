from copy import deepcopy
from quopri import decodestring

from pattenrs.behavioral_patterns import ConsoleWriter, Subject


class User:
    """
    Класс-абстракция для создания общего пользовательского интерфейса.
    """
    pass


class Developer(User):
    """
    Класс — интерфейс пользователей-разработчиков игр.
    """
    pass


class Customer(User):
    """
    Класс — интерфейс пользователей-покупателей игр.
    """
    pass


class UserFactory:
    """
    Класс-фабрика, основная задача которого вернуть конкретную
    реализацию абстрактного класса User на основе внешней информации.
    """
    types = {
        'developer': Developer,
        'customer': Customer,
    }

    @classmethod
    def create(cls, type_):
        return cls.types[type_]()


class GamePrototype:
    """
    Класс-прототип, основная задача которого — создание
    новых объектов путём копирования самого себя.
    """

    def clone(self):
        return deepcopy(self)


class Game(GamePrototype):
    """
    Класс - общий интерфейс игр.
    """

    def __init__(self, name, description, price, release_date, categories):
        self.name = name
        self.description = description
        self.price = price
        self.release_date = release_date
        self.categories = categories

        for category in categories:
            category.games.append(self)
            category.notify()


class Category(Subject):
    """
    Класс-интерфейс категорий игр.
    """
    auto_id = 0

    def __init__(self, name, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.main_category = category
        self.sub_categories = []
        self.games = []
        super().__init__()

        if self.main_category:
            self.main_category.sub_categories.append(self)

    def games_count(self):
        """
        Метод, подсчитывающий общее количество игр категории.

        :return: Кол-во игр в категории.
        """
        result = len(self.games)
        if self.sub_categories:
            for category in self.sub_categories:
                result += category.games_count()
        return result


class Engine:
    """
    Класс — основной интерфейс проекта.
    """

    def __init__(self):
        self.developers = []
        self.customers = []
        self.games = []
        self.categories = []

    @staticmethod
    def create_user(type_):
        return UserFactory.create(type_)

    def create_category(self, name, main_category):
        for category in self.categories:
            if name == category.name:
                raise ValueError(f'Категория с таким именем уже существует. Отмена операции.')
        return Category(name, main_category)

    def find_category_by_id(self, request_id):
        """
        Метод поиска категории по-соответствующему ей id.

        :param request_id: id категории.
        :return: объект класса Category, содержащий имя категории, список игр категории,
        а так же имя родительской категории (если данная категория является подкатегорией)
        """
        for item in self.categories:
            if item.id == request_id:
                return item
        raise ValueError(f'Категория с id = {request_id} отсутствует в базе данных.')

    def create_game(self, name, description, price, release_date, categories):
        for game in self.games:
            if name == game.name:
                raise ValueError(f'Игра с таким именем уже существует. Отмена операции.')
        return Game(name, description, price, release_date, categories)

    def get_game(self, name):
        """
        Метод, осуществляющий поиск игр в соответствии с названием игры.

        :param name: название игры.
        :return: объект класса Game, содержащий название игры, её описание,
        цену, дату выхода, и категорию.
        """
        for item in self.games:
            if item.name == name:
                return item
        return None

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = decodestring(val_b)
        return val_decode_str.decode('UTF-8')


class LoggerNameVerifier(type):
    """
    Метакласс, основная задача которого — проверка имени логгера.
    """

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=LoggerNameVerifier):
    """
    Класс-логгер.
    """

    def __init__(self, name, writer=ConsoleWriter()):
        self.name = name
        self.writer = writer

    def log(self, text):
        text = f'Log-----> {text}'
        self.writer.write(text)
