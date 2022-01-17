from views import Index, Store, About, Contacts, CategoryCreate, GameCreate, GameCopy


def other_front(request):
    request['key'] = 'value'


fronts = (other_front,)

routes = {
    '/': Index(),
    '/index/': Index(),
    '/store/': Store(),
    '/create-category/': CategoryCreate(),
    '/create-game/': GameCreate(),
    '/copy-game/': GameCopy(),
    '/about/': About(),
    '/contacts/': Contacts(),
}
