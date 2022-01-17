from roach_framework.templator import render
from pattenrs.creational_patterns import Engine, Logger

interface = Engine()
logger = Logger('views')


class Index:
    def __call__(self, request):
        logger.log('Запрос начальной страницы.')
        return '200 OK', render('index.html', title='Welcome')


class Store:
    def __call__(self, request):
        logger.log('Запрос страницы магазина.')
        return '200 OK', render('store.html',
                                title='Store',
                                categories=interface.categories,
                                games=interface.games)


class About:
    def __call__(self, request):
        logger.log('Запрос страницы дополнительной информации.')
        return '200 OK', render('about.html', title='About Us')


class Contacts:
    def __call__(self, request):
        logger.log('Запрос страницы контактных данных и формы общения.')
        return '200 OK', render('contact.html', title='Contacts')


class CategoryCreate:
    def __call__(self, request):

        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = interface.decode_value(name)

            if data['category']:
                category = interface.find_category_by_id(int(data['category']))
            else:
                category = None

            new_category = interface.create_category(name, category)

            interface.categories.append(new_category)

            return '200 OK', render('store.html',
                                    title='Store',
                                    categories=interface.categories,
                                    games=interface.games)
        else:
            return '200 OK', render('create_category.html',
                                    title='Create Category',
                                    categories=interface.categories)


class GameCreate:
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = interface.decode_value(name)

            description = data['description']
            description = interface.decode_value(description)

            price = data['price']
            release_date = data['release_date']

            categories = []

            for el in data['categories']:
                category = interface.find_category_by_id(int(el))
                categories.append(category)

            new_game = interface.create_game(name,
                                             description,
                                             price,
                                             release_date,
                                             categories)
            interface.games.append(new_game)

            return '200 OK', render('store.html',
                                    title='Store',
                                    categories=interface.categories,
                                    games=interface.games)
        else:
            return '200 OK', render('create_game.html',
                                    title='Create Game',
                                    categories=interface.categories)


class GameCopy:
    def __call__(self, request):
        request_params = request['request_params']

        name = request_params['name']
        game_to_copy = interface.get_game(name)
        if game_to_copy:
            new_game_name = f'Copy_of_{name}'
            new_game = game_to_copy.clone()
            new_game.name = new_game_name

            categories = []

            for el in new_game.categories:
                category = interface.find_category_by_id(int(el.id))
                categories.append(category)

            new_game_instance = interface.create_game(new_game.name,
                                                      new_game.description,
                                                      new_game.price,
                                                      new_game.release_date,
                                                      categories)

            interface.games.append(new_game_instance)

        return '200 OK', render('store.html',
                                title='Store',
                                categories=interface.categories,
                                games=interface.games)
