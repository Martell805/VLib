from overloading import Overloading, overload


class A(Overloading):
    @overload
    def f(self):
        print('A.f void overload')

    @overload
    def f(self, x: int):
        print('A.f int overload', x)

    @overload
    def f(self, x: str):
        print('A.f str overload', x)

    @overload
    def f(self, x, y):
        print('A.f two arg overload', x, y)


class B(A):
    @overload
    def f(self, x: int):
        print('B.f int overload', x)

    @overload
    def f(self, x: list):
        print('B.f list overload', x)


a = A()
print(a.f)
a.f()
a.f(1)
a.f("q")
a.f(23, False)
b = B()
b.f(4)
b.f([1, 2, 3])
