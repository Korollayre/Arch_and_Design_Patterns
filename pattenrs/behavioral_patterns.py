from abc import ABCMeta, abstractmethod


class Observer(metaclass=ABCMeta):

    @abstractmethod
    def update(self, subject):
        pass


class AddGameEmailNotifier(Observer):
    def update(self, subject):
        print(f'--- EMAIL NOTIFIER --- \n'
              f'Игра {subject.games[-1]} была добавлена в категорию {subject.name}!')


class ConsoleWriter:
    """
    Класс, основная задача которого -
    вывод в консоль сообщений логгера
    """

    @staticmethod
    def write(text):
        print(text)


class FileWriter:
    """
    Класс, основная задача которого -
    запись сообщений логгера в файл self.file_name
    директории self.folder_name
    """

    def __init__(self):
        self.folder_name = 'logs'
        self.file_name = 'log.txt'

    def write(self, text):
        with open(f'{self.folder_name}/{self.file_name}', 'a', encoding='UTF-8') as file:
            file.write(f'{text}\n')
