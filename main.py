from decorators import Property


class Kek:
    @Property
    def x(self):
        print(3)


kek = Kek()
kek.x
