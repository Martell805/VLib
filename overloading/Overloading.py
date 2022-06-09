import inspect


class NoMatchingOverload(Exception):
    """Exception thrown then there is no matching overload in object"""
    pass


def overload(f):
    """Decorator which makes functions able to overload"""
    assert callable(f), "Object must be callable"

    f.__overloaded__ = True
    return f


class OverloadList(list):
    """List storing overloaded functions"""
    def append(self, value):
        assert callable(value), "Stored value must be callable"
        assert getattr(value, "__overloaded__", False), "Function must be marked as @overload"
        super().append(value)


class OverloadDict(dict):
    """Dict representing namespace of object with overloading. Overloaded function must be marked as @overload"""
    def __setitem__(self, key, value):
        assert isinstance(key, str), "Key must be string"

        if not getattr(value, "__overloaded__", False):
            super().__setitem__(key, value)
            return

        if key not in super().keys():
            super().__setitem__(key, OverloadList())
        super().__getitem__(key).append(value)


class OverloadFunction:
    """Class represents overloaded function"""
    def __init__(self, instance, overload_list: OverloadList):
        assert isinstance(overload_list, OverloadList), "OverloadList must be passed"
        assert overload_list, "OverloadList must not be empty"

        self.instance = instance
        self.overload_list = list(reversed(overload_list))
        self.signatures = [inspect.signature(ol) for ol in self.overload_list]

        self.__name__ = self.overload_list[0].__name__

    @staticmethod
    def __signature_matches(signature: inspect.Signature, bound_args: inspect.BoundArguments):
        for name, arg in bound_args.arguments.items():
            param = signature.parameters[name]
            hint = param.annotation
            if not (hint is inspect.Parameter.empty or isinstance(arg, hint)):
                return False
        return True

    def __repr__(self):
        return f"{self.__class__.__qualname__} {self.__name__}({self.overload_list!r})"

    def __call__(self, *args, **kwargs):
        for ol, signature in zip(self.overload_list, self.signatures):
            try:
                bound_args = signature.bind(self.instance, *args, **kwargs)
                bound_args.apply_defaults()
            except TypeError:
                pass
            else:
                if self.__signature_matches(signature, bound_args):
                    return ol(self.instance, *args, **kwargs)
        raise NoMatchingOverload(f"No matching overload for {self.instance} in {self.signatures}")


class Overload:
    """Class represents property with overloaded function"""
    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name

    def __init__(self, overload_list: OverloadList):
        assert isinstance(overload_list, OverloadList), "OverloadList must be passed"
        assert overload_list, "OverloadList must not be empty"
        self.overload_list = overload_list

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.overload_list!r})"

    def __get__(self, instance, owner):
        return OverloadFunction(instance, self.overload_list)


class OverloadMeta(type):
    """Metaclass which allows to overload functions.
    You need to mark overloading functions with @overload decorator"""
    @classmethod
    def __prepare__(mcs, name, bases):
        namespace = OverloadDict()
        for base in bases:
            for key, value in base.__dict__.items():
                if isinstance(value, Overload):
                    for func in value.overload_list:
                        namespace[key] = func
        return namespace

    def __new__(mcs, name, bases, namespace, **kwargs):
        overload_namespace = {
            key: Overload(val) if isinstance(val, OverloadList) else val
            for key, val in namespace.items()
        }
        return super().__new__(mcs, name, bases, overload_namespace, **kwargs)


class Overloading(metaclass=OverloadMeta):
    pass
