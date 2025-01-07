from math import sqrt, atan2, cos, sin

def cart2cyl(x: float, y: float, z: float) -> list[float]:
    rho = sqrt(x**2 + y**2)
    φ = atan2(y, x)
    return (rho, φ, z)

def cyl2cart(rho: float, φ: float, z: float) -> list[float]:
    x = rho * cos(φ)
    y = rho * sin(φ)
    return (x, y, z)

def midpoint(a: list[float], b: list[float]) -> list[float]:
    pt = [(a[i] + b[i]) / 2 for i in range(min(len(a), len(b)))]
    return pt