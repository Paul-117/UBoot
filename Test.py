from datetime import datetime
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
from random import randrange

x_data, y_data = [], []

figure = pyplot.figure()
line, = pyplot.plot_date(x_data, y_data, '-')

def update(frame):
    x_data.append(datetime.now())
    y_data.append(randrange(0, 100))
    line.set_data(x_data, y_data)
    figure.gca().relim()
    figure.gca().autoscale_view()
    return line,

animation = FuncAnimation(figure, update, interval=200)



x_data, y_data = [], []

figure2 = pyplot.figure()
line, = pyplot.plot_date(x_data, y_data, '-')

def update2(frame):
    x_data.append(datetime.now())
    y_data.append(randrange(0, 100))
    line.set_data(x_data, y_data)
    figure2.gca().relim()
    figure2.gca().autoscale_view()
    return line,

animation = FuncAnimation(figure2, update2, interval=200)

pyplot.show()