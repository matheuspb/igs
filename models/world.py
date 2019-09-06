""" This module contains the World class. """

class World:
    """ Contains all objects that are supposed to be drawn in the viewport. """

    def __init__(self):
        self._objects = dict()

    def __getitem__(self, name):
        return self._objects[name]

    @property
    def objects(self):
        """ Returns the set of objects. """
        return self._objects.values()

    def add_object(self, obj):
        """ Adds a new object. """
        self._objects[obj.name] = obj
