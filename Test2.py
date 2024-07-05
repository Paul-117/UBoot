import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

dx, dv, N, Nb, decp = 2, 1.5, 10, 12, int(1)

Px = np.arange(Nb)
Pd = np.random.randn(N, Nb)
Vd = np.random.randn(N, Nb)

fig1, ax1 = plt.subplots(figsize=(8, 6))


def animatex(i):
    ax1.clear()
    ax1.bar(Px, Pd[i, :], width=dx / 4, align='edge', color='b')
anix = FuncAnimation(fig1, animatex, repeat=True, interval=200, frames=N)

fig2, ax2 = plt.subplots(figsize=(8, 6))


def animatev(i):
    ax2.clear()
    ax2.bar(Px, Vd[i, :], width = dv / 4, align='edge', color='b')
aniv = FuncAnimation(fig2, animatev, repeat=True, interval=200, frames=N)

plt.show()