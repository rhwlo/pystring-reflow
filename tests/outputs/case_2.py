valid, interpolation = 12, 16

def variable():
    return 2

class with_some:
    operators = 9

print(
    f"This is a multi-line f-string but it has "
    f"{valid + variable() * interpolation / using.operators} at a point that "
    f"we would otherwise want to break it."
)