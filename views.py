from roach_framework.templator import render
from pattenrs.creational_patterns import Engine, Logger
from pattenrs.structural_patterns import AppRoute, TimeDeco

INTERFACE = Engine()
LOGGER = Logger('views')

ROUTES = {}


@AppRoute(routes=ROUTES, url='/index/')
class Index:
    @TimeDeco(name='Index')
    def __call__(self, request):
        LOGGER.log('Запрос начальной страницы.')
        return '200 OK', render('index.html', title='Welcome')


@AppRoute(routes=ROUTES, url='/store/')
class Store:
    @TimeDeco(name='Store')
    def __call__(self, request):
        LOGGER.log('Запрос страницы магазина.')
        return '200 OK', render('store.html',
                                title='Store',
                                categories=INTERFACE.categories,
                                games=INTERFACE.games)


@AppRoute(routes=ROUTES, url='/about/')
class About:
    @TimeDeco(name='About')
    def __call__(self, request):
        LOGGER.log('Запрос страницы дополнительной информации.')
        return '200 OK', render('about.html', title='About Us')


@AppRoute(routes=ROUTES, url='/contacts/')
class Contacts:
    @TimeDeco(name='Contacts')
    def __call__(self, request):
        LOGGER.log('Запрос страницы контактных данных и формы общения.')
        return '200 OK', render('contact.html', title='Contacts')


@AppRoute(routes=ROUTES, url='/create-category/')
class CategoryCreate:
    @TimeDeco(name='CategoryCreate')
    def __call__(self, request):

        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = INTERFACE.decode_value(name)

            if data['category']:
                category = INTERFACE.find_category_by_id(int(data['category']))
            else:
                category = None

            new_category = INTERFACE.create_category(name, category)

            INTERFACE.categories.append(new_category)

            return '200 OK', render('store.html',
                                    title='Store',
                                    categories=INTERFACE.categories,
                                    games=INTERFACE.games)
        else:
            return '200 OK', render('create_category.html',
                                    title='Create Category',
                                    categories=INTERFACE.categories)


@AppRoute(routes=ROUTES, url='/create-game/')
class GameCreate:
    @TimeDeco(name='GameCreate')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = INTERFACE.decode_value(name)

            description = data['description']
            description = INTERFACE.decode_value(description)

            price = data['price']
            release_date = data['release_date']

            categories = []

            for el in data['categories']:
                category = INTERFACE.find_category_by_id(int(el))
                categories.append(category)

            new_game = INTERFACE.create_game(name,
                                             description,
                                             price,
                                             release_date,
                                             categories)
            INTERFACE.games.append(new_game)

            return '200 OK', render('store.html',
                                    title='Store',
                                    categories=INTERFACE.categories,
                                    games=INTERFACE.games)
        else:
            return '200 OK', render('create_game.html',
                                    title='Create Game',
                                    categories=INTERFACE.categories)


@AppRoute(routes=ROUTES, url='/copy-game/')
class GameCopy:
    @TimeDeco(name='GameCopy')
    def __call__(self, request):
        request_params = request['request_params']

        name = request_params['name']
        game_to_copy = INTERFACE.get_game(name)
        if game_to_copy:
            new_game_name = f'Copy_of_{name}'
            new_game = game_to_copy.clone()
            new_game.name = new_game_name

            categories = []

            for el in new_game.categories:
                category = INTERFACE.find_category_by_id(int(el.id))
                categories.append(category)

            new_game_instance = INTERFACE.create_game(new_game.name,
                                                      new_game.description,
                                                      new_game.price,
                                                      new_game.release_date,
                                                      categories)

            INTERFACE.games.append(new_game_instance)

        return '200 OK', render('store.html',
                                title='Store',
                                categories=INTERFACE.categories,
                                games=INTERFACE.games)
