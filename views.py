from roach_framework.templator import render
from pattenrs.creational_patterns import Engine, Logger
from pattenrs.structural_patterns import AppRoute, TimeDeco
from pattenrs.behavioral_patterns import AddGameEmailNotifier, ListView, CreateView, BaseSerializer

LOGGER = Logger('views')

INTERFACE = Engine()

EMAIL_NOTIFIER = AddGameEmailNotifier()

ROUTES = {}


@AppRoute(routes=ROUTES, url='/')
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

            new_category.observers.append(EMAIL_NOTIFIER)

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


@AppRoute(routes=ROUTES, url='/games-list/')
class GamesListView(ListView):
    template_name = 'games_list.html'
    context_object_name = 'games'

    def get_request_params(self):
        return self.request['request_params']

    def get_context_data(self):
        context = super().get_context_data()
        context['title'] = 'Games List'
        context['category_id'] = self.get_request_params()['id']
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.clear()
        category = INTERFACE.find_category_by_id(int(self.get_request_params()['id']))
        queryset.extend(category.games)
        if category.sub_categories:
            for sub_category in category.sub_categories:
                queryset.extend(sub_category.games)
        return queryset


@AppRoute(routes=ROUTES, url='/add-game/')
class GameCreateView(CreateView):
    template_name = 'add_game.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['title'] = 'Game Adding'
        category_id = int(self.request['request_params']['id'])
        context['category'] = INTERFACE.find_category_by_id(category_id)
        return context

    def create_obj(self, data: dict):
        name = data['name']
        name = INTERFACE.decode_value(name)

        description = data['description']
        description = INTERFACE.decode_value(description)

        price = data['price']
        release_date = data['release_date']

        category = [INTERFACE.find_category_by_id(int(data['category']))]

        new_game = INTERFACE.create_game(name,
                                         description,
                                         price,
                                         release_date,
                                         category)
        INTERFACE.games.append(new_game)


@AppRoute(routes=ROUTES, url='/categories-api/')
class CategoriesApi:
    @TimeDeco(name='CategoriesApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(INTERFACE.categories).save()


@AppRoute(routes=ROUTES, url='/games-api/')
class GamesApi:
    @TimeDeco(name='GamesApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(INTERFACE.games).save()
