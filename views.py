from copy import deepcopy

from roach_framework.templator import render
from pattenrs.creational_patterns import Engine, Logger, MapperRegistry
from pattenrs.structural_patterns import AppRoute, TimeDeco
from pattenrs.behavioral_patterns import AddGameEmailNotifier, ListView, CreateView, BaseSerializer
from pattenrs.unit_of_work import UnitOfWork

LOGGER = Logger('views')

ENGINE = Engine()

EMAIL_NOTIFIER = AddGameEmailNotifier()

UnitOfWork.new_current()
UnitOfWork.get_current().set_mapper_registry(MapperRegistry)

GAME_MAPPER = MapperRegistry.get_current_mapper('game')
CATEGORY_MAPPER = MapperRegistry.get_current_mapper('category')
GAMES_CATEGORY_MAPPER = MapperRegistry.get_current_mapper('games_categories')
CATEGORY_DEPENDENCE_MAPPER = MapperRegistry.get_current_mapper('categories_dependence')

ROUTES = {}


def add_categories_to_context():
    """
    Функция, создающая список categories,
    в котором хранятся категории с их подкатегориями
    """
    all_categories = deepcopy(ENGINE.categories)

    if CATEGORY_DEPENDENCE_MAPPER.all():
        categories = []
        for item in CATEGORY_DEPENDENCE_MAPPER.all():
            main_category = CATEGORY_MAPPER.find_by_id(item[0])
            sub_category = CATEGORY_MAPPER.find_by_id(item[1])

            for el in all_categories:
                if el.id == main_category.id:
                    all_categories.remove(el)

            for el in all_categories:
                if el.id == sub_category.id:
                    all_categories.remove(el)

            main_category.sub_categories = []
            main_category.sub_categories.append(sub_category)

            categories.append(main_category)

        categories.extend(all_categories)
    else:
        categories = ENGINE.categories

    return categories


@AppRoute(routes=ROUTES, url='/')
class Index:
    @TimeDeco(name='Index')
    def __call__(self, request):
        LOGGER.log('Запрос начальной страницы.')
        return '200 OK', render('index.html', title='Welcome')


@AppRoute(routes=ROUTES, url='/store/')
class Store(ListView):
    template_name = 'store.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['title'] = 'Store'
        context['games'] = GAME_MAPPER.all()
        context['categories'] = add_categories_to_context()

        return context


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
class CategoryCreate(CreateView):
    template_name = 'create_category.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['title'] = 'Create Category'
        context['categories'] = ENGINE.categories
        return context

    def create_obj(self, data: dict):
        name = data['name']
        name = ENGINE.decode_value(name)

        new_category = ENGINE.create_category(name)

        if data['category']:
            main_category = ENGINE.find_category_by_id(int(data['category']))
            new_category_dependence_row = ENGINE.create_category_dependence(main_category.id, new_category.id)
            new_category_dependence_row.mark_new()
            ENGINE.categories_dependence.append(new_category_dependence_row)

        new_category.observers.append(EMAIL_NOTIFIER)

        ENGINE.categories.append(new_category)

        new_category.mark_new()

        UnitOfWork.get_current().commit()


@AppRoute(routes=ROUTES, url='/create-game/')
class GameCreate:
    @TimeDeco(name='GameCreate')
    def __call__(self, request):
        if request['method'] == 'POST':
            data = request['data']

            name = data['name']
            name = ENGINE.decode_value(name)

            description = data['description']
            description = ENGINE.decode_value(description)

            price = data['price']
            release_date = data['release_date']

            categories = []

            for el in data['categories']:
                category = ENGINE.find_category_by_id(int(el))
                categories.append(category)

            new_game = ENGINE.create_game(name,
                                          description,
                                          price,
                                          release_date)
            new_game.mark_new()

            for el in categories:
                new_game_category_row = ENGINE.create_game_category(new_game.id, el.id)
                new_game_category_row.mark_new()
                ENGINE.games_categories.append(new_game_category_row)

            ENGINE.games.append(new_game)

            UnitOfWork.get_current().commit()

            return '200 OK', render('store.html',
                                    title='Store',
                                    categories=add_categories_to_context(),
                                    games=ENGINE.games)
        else:
            return '200 OK', render('create_game.html',
                                    title='Create Game',
                                    categories=add_categories_to_context())


@AppRoute(routes=ROUTES, url='/copy-game/')
class GameCopy:
    @TimeDeco(name='GameCopy')
    def __call__(self, request):
        request_params = request['request_params']

        name = request_params['name']
        game_to_copy = ENGINE.get_game(name)
        if game_to_copy:
            new_game_name = f'Copy_of_{name}'
            new_game = game_to_copy.clone()
            new_game.name = new_game_name

            categories = GAMES_CATEGORY_MAPPER.find_by_game_id(game_to_copy.id)

            new_game_instance = ENGINE.create_game(new_game.name,
                                                   new_game.description,
                                                   new_game.price,
                                                   new_game.release_date)

            for el in categories:
                new_game_category_row = ENGINE.create_game_category(new_game_instance.id, el.id)
                new_game_category_row.mark_new()
                ENGINE.games_categories.append(new_game_category_row)

            new_game_instance.mark_new()

            ENGINE.games.append(new_game_instance)

            UnitOfWork.get_current().commit()

        return '200 OK', render('store.html',
                                title='Store',
                                categories=add_categories_to_context(),
                                games=ENGINE.games)


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

        category = CATEGORY_MAPPER.find_by_id(self.get_request_params()['id'])
        category_games = GAMES_CATEGORY_MAPPER.find_by_category_id(category.id)
        queryset.extend(category_games)

        sub_categories = CATEGORY_DEPENDENCE_MAPPER.find_by_main_category_id(category.id)
        if sub_categories:
            for sub_category in sub_categories:
                sub_category_games = GAMES_CATEGORY_MAPPER.find_by_category_id(sub_category.id)
                queryset.extend(sub_category_games)
        return queryset


@AppRoute(routes=ROUTES, url='/add-game/')
class GameCreateView(CreateView):
    template_name = 'add_game.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['title'] = 'Game Adding'
        category_id = int(self.request['request_params']['id'])
        context['category'] = ENGINE.find_category_by_id(category_id)
        return context

    def create_obj(self, data: dict):
        name = data['name']
        name = ENGINE.decode_value(name)

        description = data['description']
        description = ENGINE.decode_value(description)

        price = data['price']
        release_date = data['release_date']

        category = ENGINE.find_category_by_id(int(data['category']))

        new_game = ENGINE.create_game(name,
                                      description,
                                      price,
                                      release_date)

        new_game.mark_new()

        new_game_category_row = ENGINE.create_game_category(new_game.id, category.id)

        new_game_category_row.mark_new()

        ENGINE.games.append(new_game)
        ENGINE.games_categories.append(new_game_category_row)

        UnitOfWork.get_current().commit()


@AppRoute(routes=ROUTES, url='/categories-api/')
class CategoriesApi:
    @TimeDeco(name='CategoriesApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(ENGINE.categories).save()


@AppRoute(routes=ROUTES, url='/games-api/')
class GamesApi:
    @TimeDeco(name='GamesApi')
    def __call__(self, request):
        return '200 OK', BaseSerializer(ENGINE.games).save()
