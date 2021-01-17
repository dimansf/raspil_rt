class A:
    a=0
 
    def __init__(self, a):
        self.a=a
       



b=[A(1), A(2), A(3)]
c=[A(1), A(1), A(1)]

b.clear()
b.extend(c)

print(b)


class B:
    c = property()
    def __init__(self) -> None:
        print(self.c)


class C:
    d = 10
    def __init__(self, d) -> None:
        self.d = d
    def __lt__(self, o):
        return self.d < o.d 

d1 = C(5)
d2 = C(10)

print(d1 < d2)