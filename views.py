from roach_framework.temlator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', title='Welcome')


class About:
    def __call__(self, request):
        return '200 OK', render('about.html', title='About Us')


class Contacts:
    def __call__(self, request):
        return '200 OK', render('contact.html', title='Contacts')
