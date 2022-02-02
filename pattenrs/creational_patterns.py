import itertools
from copy import deepcopy
from sqlite3 import connect
from quopri import decodestring

from pattenrs.errors import *
from pattenrs.behavioral_patterns import ConsoleWriter, Subject
from pattenrs.unit_of_work import DomainObject

CONNECTION = connect('db.sqlite')


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


class Game(GamePrototype, DomainObject):
    """
    Класс - общий интерфейс игр.
    """
    auto_id = 1

    def __init__(self, name, description, price, release_date, new_game=True):
        if new_game:
            self.id = Game.auto_id
            Game.auto_id += 1
        self.name = name
        self.description = description
        self.price = price
        self.release_date = release_date


class GameMapper:
    def __init__(self, conn):
        self.connection = conn
        self.cursor = self.connection.cursor()
        self.table_name = 'games'

    def all(self):
        statement = f'SELECT * from {self.table_name}'
        self.cursor.execute(statement)
        res = []
        for item in self.cursor.fetchall():
            game = Game(*item[1:], new_game=False)
            game.id = item[0]
            res.append(game)
        return res

    def find_by_id(self, obj_id):
        statement = f'SELECT * FROM {self.table_name} WHERE id = ?'
        self.cursor.execute(statement, (str(obj_id),))
        res = self.cursor.fetchone()
        game = Game(*res[1:], new_game=False)
        game.id = res[0]
        return game

    def insert(self, obj):
        statement = f'INSERT INTO {self.table_name} ' \
                    f'(name, description, price, release_date) ' \
                    f'VALUES (?,?,?,?)'
        self.cursor.execute(statement, (obj.name,
                                        obj.description,
                                        obj.price,
                                        obj.release_date))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f'UPDATE {self.table_name} ' \
                    f'SET name = ?, description = ?, price = ?, release_date = ? ' \
                    f'WHERE id = ?'
        self.cursor.execute(statement, (obj.name,
                                        obj.description,
                                        obj.price,
                                        obj.release_date,
                                        obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj_id):
        statement = f'DELETE FROM {self.table_name} WHERE id = ?'
        self.cursor.execute(statement, (str(obj_id),))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


class Category(Subject, DomainObject):
    """
    Класс-интерфейс категорий игр.
    """
    auto_id = 1

    def __init__(self, name, new_category=True):
        if new_category:
            self.id = Category.auto_id
            Category.auto_id += 1
        self.name = name
        super().__init__()

    def games_count(self):
        """
        Метод, подсчитывающий общее количество игр категории.

        :return: Кол-во игр в категории.
        """

        games_categories_mapper = MapperRegistry.get_current_mapper('games_categories')
        categories_dependence_mapper = MapperRegistry.get_current_mapper('categories_dependence')

        games = games_categories_mapper.find_by_category_id(self.id)
        res = len(games)

        sub_categories = categories_dependence_mapper.find_by_main_category_id(self.id)
        if sub_categories:
            for sub_category in sub_categories:
                sub_category_games = games_categories_mapper.find_by_category_id(sub_category.id)
                res += len(sub_category_games)

        return res


class CategoryMapper:
    def __init__(self, conn):
        self.connection = conn
        self.cursor = self.connection.cursor()
        self.table_name = 'categories'

    def all(self):
        statement = f'SELECT * from {self.table_name}'
        self.cursor.execute(statement)
        res = []
        for item in self.cursor.fetchall():
            category = Category(*item[1:], new_category=False)
            category.id = item[0]
            res.append(category)
        return res

    def find_by_id(self, obj_id):
        statement = f'SELECT * FROM {self.table_name} WHERE id = ?'
        self.cursor.execute(statement, (str(obj_id),))
        res = self.cursor.fetchone()
        category = Category(*res[1:], new_category=False)
        category.id = res[0]
        return category

    def insert(self, obj):
        statement = f'INSERT INTO {self.table_name} ' \
                    f'(name) VALUES (?)'
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def update(self, obj):
        statement = f'UPDATE {self.table_name} ' \
                    f'SET name = ? WHERE id = ?'
        self.cursor.execute(statement, (obj.name,
                                        obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj_id):
        statement = f'DELETE FROM {self.table_name} WHERE id = ?'
        self.cursor.execute(statement, (str(obj_id),))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


class GamesCategoryModel(DomainObject):
    def __init__(self, game_id, category_id):
        self.game_id = game_id
        self.category_id = category_id


class GamesCategoryMapper:
    def __init__(self, conn):
        self.connection = conn
        self.cursor = self.connection.cursor()
        self.table_name = 'games_categories'

    def all(self):
        statement = f'SELECT * from {self.table_name}'
        self.cursor.execute(statement)
        res = []
        for item in self.cursor.fetchall():
            new_dict = dict()
            new_dict['game_id'], new_dict['category_id'] = item[0], item[1]
            res.append(new_dict)
        return res

    def find_by_category_id(self, obj_id):
        statement = f'SELECT * FROM {self.table_name} WHERE category_id = ?'
        self.cursor.execute(statement, (str(obj_id),))
        rows = self.cursor.fetchall()
        res = []
        for item in rows:
            mapper = MapperRegistry.get_current_mapper('game')
            game = mapper.find_by_id(item[0])
            res.append(game)
        return res

    def find_by_game_id(self, obj_id):
        statement = f'SELECT * FROM {self.table_name} WHERE game_id = ?'
        self.cursor.execute(statement, (str(obj_id),))
        rows = self.cursor.fetchall()
        res = []
        for item in rows:
            mapper = MapperRegistry.get_current_mapper('category')
            category = mapper.find_by_id(item[1])
            res.append(category)
        return res

    def insert(self, obj):
        statement = f'INSERT INTO {self.table_name} ' \
                    f'(game_id, category_id) ' \
                    f'VALUES (?,?)'
        self.cursor.execute(statement, (obj.game_id,
                                        obj.category_id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def delete(self, obj_id):
        statement = f'DELETE FROM {self.table_name} WHERE id = ?'
        self.cursor.execute(statement, (str(obj_id),))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


class CategoriesDependenceModel(DomainObject):
    def __init__(self, main_category_id, sub_category_id):
        self.main_category_id = main_category_id
        self.sub_category_id = sub_category_id


class CategoriesDependenceMapper:
    def __init__(self, conn):
        self.connection = conn
        self.cursor = self.connection.cursor()
        self.table_name = 'categories_dependence'

    def all(self):
        statement = f'SELECT * from {self.table_name}'
        self.cursor.execute(statement)
        res = []
        for item in self.cursor.fetchall():
            res.append(item)
        return res

    def find_by_main_category_id(self, obj_id):
        statement = f'SELECT * FROM {self.table_name} WHERE main_category_id = ?'
        self.cursor.execute(statement, (str(obj_id),))
        rows = self.cursor.fetchall()
        res = []
        for item in rows:
            mapper = MapperRegistry.get_current_mapper('category')
            category = mapper.find_by_id(item[1])
            res.append(category)
        return res

    def insert(self, obj):
        statement = f'INSERT INTO {self.table_name} ' \
                    f'(main_category_id, sub_category_id) ' \
                    f'VALUES (?,?)'
        self.cursor.execute(statement, (obj.main_category_id,
                                        obj.sub_category_id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbCommitException(e.args)

    def delete(self, obj_id):
        statement = f'DELETE FROM {self.table_name} WHERE id = ?'
        self.cursor.execute(statement, (str(obj_id),))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


class MapperRegistry:
    mappers = {
        'game': GameMapper,
        'category': CategoryMapper,
        'games_categories': GamesCategoryMapper,
        'categories_dependence': CategoriesDependenceMapper,
    }

    @staticmethod
    def get_mapper(obj):
        if isinstance(obj, Game):
            return GameMapper(CONNECTION)
        elif isinstance(obj, Category):
            return CategoryMapper(CONNECTION)
        elif isinstance(obj, GamesCategoryModel):
            return GamesCategoryMapper(CONNECTION)
        elif isinstance(obj, CategoriesDependenceModel):
            return CategoriesDependenceMapper(CONNECTION)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](CONNECTION)


class Engine:
    """
    Класс — основной интерфейс проекта.
    """

    def __init__(self):
        category_mapper = MapperRegistry.get_current_mapper('category')
        games_mapper = MapperRegistry.get_current_mapper('game')
        games_categories_mapper = MapperRegistry.get_current_mapper('games_categories')
        categories_dependence_mapper = MapperRegistry.get_current_mapper('categories_dependence')

        self.categories = category_mapper.all()
        self.games = games_mapper.all()
        self.games_categories = games_categories_mapper.all()
        self.categories_dependence = categories_dependence_mapper.all()
        self.developers = []
        self.customers = []

    @staticmethod
    def create_user(type_):
        return UserFactory.create(type_)

    def create_category(self, name):
        for category in self.categories:
            if name == category.name:
                raise ValueError(f'Категория с таким именем уже существует. Отмена операции.')
        return Category(name)

    @staticmethod
    def create_category_dependence(main_category_id, sub_category_id):
        return CategoriesDependenceModel(main_category_id, sub_category_id)

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

    def create_game(self, name, description, price, release_date):
        for game in self.games:
            if name == game.name:
                raise ValueError(f'Игра с таким именем уже существует. Отмена операции.')
        return Game(name, description, price, release_date)

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
    def create_game_category(game_id, category_id):
        return GamesCategoryModel(game_id, category_id)

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
