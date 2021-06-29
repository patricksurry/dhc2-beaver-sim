from random import random
from datetime import datetime


def datetimeGenerator():
    while True:
        yield datetime.now().isoformat()


def timeGenerator():
    while True:
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yield (now - midnight).total_seconds()


def forceSeriesGenerator(min=0, max=1, fmax=0.01, damping=0.9, wrap=False):
    x = random()
    v = 0
    while True:
        yield x * (max - min) + min
        x += v
        v += (2*random()-1)*fmax
        v *= damping
        if x < 0 or x > 1:
            if not wrap:
                v = -v
                x = -x if x < 0 else 2-x
            else:
                x = x - 1 if x > 1 else x + 1


def categoricalGenerator(values):
    n = len(values)
    vs = forceSeriesGenerator(min=0, max=n, wrap=True)
    while True:
        yield values[min(int(next(vs)), n-1)]


metricGenerators = dict(
    time=timeGenerator(),
    date=datetimeGenerator(),
    atmosphericPressure=forceSeriesGenerator(955, 1075),
    altitude=forceSeriesGenerator(0, 30000, fmax=0.001),
    pitch=forceSeriesGenerator(-25, 25),
    roll=forceSeriesGenerator(-25, 25),
    heading=forceSeriesGenerator(0, 360, wrap=True),
    radialDeviation=forceSeriesGenerator(-10, 10),
    radialVOR=forceSeriesGenerator(0, 360, wrap=True),
    headingADF=forceSeriesGenerator(0, 360, wrap=True),
    relativeADF=forceSeriesGenerator(0, 360, wrap=True),
    verticalSpeed=forceSeriesGenerator(-1500, 1500),
    turnrate=forceSeriesGenerator(-3, 3),
    airspeed=forceSeriesGenerator(40, 200),
    suctionPressure=forceSeriesGenerator(0, 10),
    manifoldPressure=forceSeriesGenerator(10, 50),
    fuelFront=forceSeriesGenerator(0, 26),
    fuelCenter=forceSeriesGenerator(0, 26),
    fuelRear=forceSeriesGenerator(0, 20),
    fuelSelector=categoricalGenerator(['front', 'center', 'rear']),
    engineTachometer=forceSeriesGenerator(300, 3500),
    oilPressure=forceSeriesGenerator(0, 200),
    fuelPressure=forceSeriesGenerator(0, 10),
    oilTemperature=forceSeriesGenerator(0, 100),
)


def readMetrics():
    return {k: next(v) for (k, v) in metricGenerators.items()}
