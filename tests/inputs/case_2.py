valid, interpolation = 12, 16

def variable():
    return 2

class with_some:
    operators = 9

print(
    f"This is a multi-line f-string but it has {valid + variable() * interpolation / using.operators} "
    f"at a point that we would otherwise want to break it."
)