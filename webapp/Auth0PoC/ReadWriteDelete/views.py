from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
import json
import requests


@login_required
def items(request):
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
    user = request.user
    auth0user = user.social_auth.get(provider="auth0")
    context['auth0user'] = auth0user
    context['userdata'] = json.dumps({
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture']
    })
    return render(request, 'items.html', context)


@login_required
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
            return redirect(reverse('ReadWriteDelete:items'))
    r = requests.get('http://localhost:5010/items/' + key)
    if r.status_code != 200:
        context['error_message'] = 'Item not found'
    else:
        context['item'] = r.json()
    return render(request, 'item.html', context)


def index(request):
    return render(request, 'index.html')
