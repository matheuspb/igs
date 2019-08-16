class World:

    def __init__(self, objects=None):
        self._objects = set() if objects is None else objects

    @property
    def objects(self):
        return self._objects
