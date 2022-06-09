import inspect


class Property:
    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner):
        return self.func(instance)


class MethodClass:
    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

        self.class_name = inspect.stack()[1][0].f_locals['__qualname__']
        self.instance = inspect.stack()[1][0].f_locals[self.class_name]

    def __call__(self, *args, **kwargs):
        return self.func(self.instance)
