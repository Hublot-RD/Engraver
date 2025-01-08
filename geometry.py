from math import sqrt, atan2, cos, sin

def cart2cyl(x: float, y: float, z: float) -> list[float]:
    r = sqrt(x**2 + y**2)
    φ = atan2(y, x)
    return (r, φ, z)

def cyl2cart(r: float, φ: float, z: float) -> list[float]:
    x = r * cos(φ)
    y = r * sin(φ)
    return (x, y, z)

def midpoint(a: list[float], b: list[float]) -> list[float]:
    pt = [(a[i] + b[i]) / 2 for i in range(min(len(a), len(b)))]
    return pt

def distance_cart(a: list[float], b: list[float]) -> float:
    dist = 0
    for i in range(len(a)):
        dist += (a[i] - b[i])**2
    return sqrt(dist)

def distance_cyl(a: list[float], b: list[float]) -> float:
    a = cyl2cart(*a)
    b = cyl2cart(*b)
    return distance_cart(a, b)