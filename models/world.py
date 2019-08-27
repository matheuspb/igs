""" This module contains the World class. """

class World:
    """ Contains all objects that are supposed to be drawn in the viewport. """

    def __init__(self, objects=None):
        self._objects = set() if objects is None else objects

    @property
    def objects(self):
        """ Returns the set of objects. """
        return self._objects

    def add_object(self, obj):
        """ Adds a new object. """
        self._objects.add(obj)
