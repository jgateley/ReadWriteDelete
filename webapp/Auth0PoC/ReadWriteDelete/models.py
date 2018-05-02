from django.db import models


class Item(models.Model):
    """
    Item model: items are just key/value pairs.
    """
    key = models.CharField(max_length=20, primary_key=True)
    value = models.CharField(max_length=200)

    def to_dict(self):
        """
        Convert an item to a python dictionary
        :return: the dictionary
        """
        return {'key': self.key, 'value': self.value}

    @staticmethod
    def list():
        """
        Return a list of all items ordered by key
        :return: list of items
        """
        result = []
        for item in Item.objects.all().order_by('key'):
            result.append(item.to_dict())
        return result

    @staticmethod
    def get(key):
        """
        Lookup an item by key
        :param key: the key
        :return: item as a dictionary, or None if not found
        """
        results = Item.objects.filter(key=key)
        if len(results) == 0:
            return None
        else:
            return results[0].to_dict()

    @staticmethod
    def make(key, value):
        """
        Create a new item. The key must not already exist
        :param key: new key
        :param value: new value
        :return: False if the item exists, True if the item was created
        """
        if Item.get(key) is not None:
            return False
        Item(key=key, value=value).save()
        return True

    @staticmethod
    def remove(key):
        """
        Remove an item from the database
        :param key: key of the item to remove
        :return: True if removed, false if it doesn't exist
        """
        results = Item.objects.filter(key=key)
        if len(results) == 0:
            return False
        results[0].delete()
        return True
