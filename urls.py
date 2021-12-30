from views import Index, About, Contacts


def other_front(request):
    request['key'] = 'key'


fronts = (other_front,)

routes = {
    '/': Index(),
    '/about/': About(),
    '/contacts/': Contacts(),
}
