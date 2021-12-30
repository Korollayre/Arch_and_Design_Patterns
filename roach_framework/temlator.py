from jinja2 import Template
from os.path import join


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
    file_path = join(template_folder, template_name)

    with open(file_path, encoding='utf-8') as f:
        template = Template(f.read())

    return template.render(**kwargs)
