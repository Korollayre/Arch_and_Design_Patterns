from views import Index, About, Contacts


def other_front(request):
    request['key'] = 'value'


fronts = (other_front,)

routes = {
    '/': Index(),
    '/index/': Index(),
    '/about/': About(),
    '/contacts/': Contacts(),
}
