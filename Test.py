import numpy as np
import math

def pol2cart(X, Y, d, phi):
    x = X + d * np.sin(math.radians(phi))
    y = Y - d * np.cos(math.radians(phi))
    return (round(x), round(y))

# Example usage:
X, Y, d, phi = 0, 0, 81, 420
result = pol2cart(X, Y, d, phi)
print(result)