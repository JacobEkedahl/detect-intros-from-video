## Determines the probability of an sequence to be an intro
import numpy

from pomegranate import *
from utils import file_handler, time_handler


def create():
    intros = file_handler.get_intros()
    obs = []
    labels = []

    for intro in intros:

        if intro["end"] != "00:00:00":
            temp = []
            start = time_handler.timestamp(intro["start"]) / 1000
            end = time_handler.timestamp(intro["end"]) / 1000
            size = abs(end - start)
            temp.append(start)
            temp.append(size)
            obs.append(numpy.array(temp))
            labels.append(numpy.array(1))

    model = NaiveBayes.from_samples(MultivariateGaussianDistribution, X, y)
    pred = model.predict(obs[3])
    print(pred)
