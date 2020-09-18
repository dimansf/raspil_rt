class A:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def __hash__(self) -> int:
        
        return hash(f'({self.a}, {self.b})')
    
    def __eq__(self, o: object) -> bool:
        return hash(self) == hash(o)

x1 = A(1,2)
x2 = A(1,2)
x3 = A(1,4)

print(x1 == x2)

d1 = {}

d1[x1] = 1
d1[x2] += 2
d1[x3] = 3

print(d1[x1] == 3)


