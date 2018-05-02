from django.shortcuts import redirect, render
from django.urls import reverse
import requests


def index(request):
    """
    The index view, shows all items and lets a new item be added.
    If there is POST data, it means a form was submitted and try to add the item.
    :param request: The HTTP request
    :return: a rendered view
    """
    context = {}
    if request.POST != {}:
        r = requests.post('http://localhost:5010/items',
                          json={'key': request.POST['key'], 'value': request.POST['value']})
        if r.status_code != 204:
            context['error_message'] = r.content
    r = requests.get('http://localhost:5010/items')
    context['items'] = r.json()
    return render(request, 'index.html', context)


def item(request, key):
    """
    The single item view, shows an item and lets it be deleted.
    Show a message if delete fails, otherwise redirect to the index page.
    If the item lookup fails, show a message.
    :param request: The HTTP request
    :param key: The item key
    :return:
    """
    context = {}
    if request.POST != {}:
        r = requests.delete('http://localhost:5010/items/' + key)
        if r.status_code != 204:
            context['error_message'] = r.content
        else:
            return redirect(reverse('ReadWriteDelete:index'))
    r = requests.get('http://localhost:5010/items/' + key)
    if r.status_code != 200:
        context['error_message'] = 'Item not found'
    else:
        context['item'] = r.json()
    return render(request, 'item.html', context)
