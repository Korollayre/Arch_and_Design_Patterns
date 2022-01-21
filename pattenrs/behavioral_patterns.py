from abc import ABCMeta, abstractmethod

from roach_framework.templator import render


class Observer(metaclass=ABCMeta):
    """
    Класс-абстракция описывающий необходимый
    интерфейс конкретных классов-наблюдателей.
    """

    @abstractmethod
    def update(self, subject):
        pass


class AddGameEmailNotifier(Observer):
    """
    Класс - конкретная реализация класса-абстракции Observer.
    Класс выводит в консоль сообщение о добавлении игры в категорию.
    """

    def update(self, subject):
        print(f'--- EMAIL NOTIFIER --- \n'
              f'Игра {subject.games[-1]} была добавлена в категорию {subject.name}!')


class Subject:
    """
    Класс-интерфейс, основная задача которого -
    нотификация наблюдателей observers.
    """

    def __init__(self):
        self.observers = []

    def __notify(self):
        for item in self.observers:
            item.update(self)


class TemplateView:
    """
    Класс-шаблон, содержащий базовый интерфейс для
    классов-отображений.
    """
    template_name = 'template.html'

    def get_context_data(self):
        return {}

    def get_template(self):
        return self.template_name

    def render_template_with_context(self):
        template_name = self.get_template()
        context = self.get_context_data()
        return '200 OK', render(template_name, **context)

    def __call__(self, request):
        self.request = request
        return self.render_template_with_context()


class ListView(TemplateView):
    """
    Класс-шаблон, содержащий базовый интерфейс для
    классов-отображений, основная задача которых -
    предоставление списка объектов.
    """
    queryset = []
    template_name = 'list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return self.queryset

    def get_context_object_name(self):
        return self.context_object_name

    def get_context_data(self):
        queryset = self.get_queryset()
        context_object_name = self.get_context_object_name()
        context = {context_object_name: queryset}
        return context


class CreateView(TemplateView):
    """
    Класс-шаблон, содержащий базовый интерфейс для
    классов-отображений, основная задача которых -
    отображение формы для создания объекта.
    """
    template_name = 'create.html'

    @staticmethod
    def get_request_data(request):
        return request['data']

    def create_obj(self, data: dict):
        pass

    def __call__(self, request):
        if request['method'] == 'POST':
            data = self.get_request_data(request)
            self.create_obj(data)
            return self.render_template_with_context()
        else:
            return super().__call__(request)


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
