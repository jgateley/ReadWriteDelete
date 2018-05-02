from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^items$', views.items, name='items'),
    url(r'^items/(?P<key>.+)$', views.item, name='item'),
    url(r'^index$', views.index, name='index'),
]
