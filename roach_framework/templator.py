from jinja2 import FileSystemLoader
from jinja2.environment import Environment


def render(template_name, template_folder='templates', **kwargs):
    """
    Функция для работы с шаблонизатором. Принимает имя шаблона,
    путь к файлу шаблонов, и аргументы. Возвращает отрисованную страницу
    с переданными аргументами в виде строки.

    :param template_name: имя шаблона
    :param template_folder: папка в которой ищем шаблон
    :param kwargs: параметры
    :return:
    """
    env = Environment()
    env.loader = FileSystemLoader(template_folder)
    template = env.get_template(template_name)
    return template.render(**kwargs)
