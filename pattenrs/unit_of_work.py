from threading import local


class UnitOfWork:
    """
    Класс, основная задача которого - отслеживать изменения
    данных модели, и осуществлять внесение этих изменений
    в БД в виде единой транзакции.
    """
    current = local()

    def __init__(self, mapper_registry):
        """
        Для отслеживания изменений используются 3 списка:
        self.new_objects - список новых объектов модели
        self.modify_objects - список измененных объектов модели
        self.removed_objects - список удаленных объектов модели
        """
        self.mapper_registry = mapper_registry

        self.new_objects = []
        self.modify_objects = []
        self.removed_objects = []

    def register_new(self, obj):
        """
        Метод, добавляющий новый объект в список новых объектов
        """
        self.new_objects.append(obj)

    def register_modify(self, obj):
        """
        Метод, добавляющий измененный объект в список именных объектов
        """
        self.modify_objects.append(obj)

    def register_removed(self, obj):
        """
        Метод, добавляющий удаленный объект в список удаленных объектов
        """
        self.removed_objects.append(obj)

    def insert_new(self):
        """
        Метод, осуществляющий добавление нового объекта
        в соответствующую таблицу БД
        """
        for obj in self.new_objects:
            self.mapper_registry.get_mapper(obj).insert(obj)

    def update_modified(self):
        """
        Метод, осуществляющий модификацию соответствующего объекта
        соответственной таблицы БД
        """
        for obj in self.modify_objects:
            self.mapper_registry.get_mapper(obj).update(obj)

    def delete_removed(self):
        """
        Метод, осуществляющий удаление объекта
        в соответствующей таблице БД
        """
        for obj in self.removed_objects:
            self.mapper_registry.get_mapper(obj).delete(obj)

    def commit(self):
        """
        Метод, определяющий последовательность внесения изменений
        в объекты БД, а так же очищающий списки объектов после
        внесения изменений в БД
        """
        self.insert_new()
        self.update_modified()
        self.delete_removed()

        self.new_objects.clear()
        self.modify_objects.clear()
        self.removed_objects.clear()

    @staticmethod
    def new_current():
        """
        Метод, осуществляющий создание экземпляра объекта
        класса UnitOfWork в текущем потоке.
        """
        __class__.set_current(UnitOfWork())

    @classmethod
    def set_current(cls, unit_of_work):
        cls.current.unit_of_work = unit_of_work

    @classmethod
    def get_current(cls):
        return cls.current.unit_of_work


class DomainObject:
    """
    Класс, обладающий интерфейсом для добавления, модификации
    и удалении объектов в БД путем обращения к методам
    класса UnitOfWork
    """

    def mark_new(self):
        UnitOfWork.get_current().register_new(self)

    def mark_modify(self):
        UnitOfWork.get_current().register_modify(self)

    def mark_removed(self):
        UnitOfWork.get_current().register_removed(self)
