import pickle

from game.agent.info_sets import *
from game.model.cheating_model import CheatingModel
from game.model.simple_model import SimpleModel

models = {
    'simple': SimpleModel(),
    'cheating': CheatingModel()
}

info_sets = {'std': StandardGenerator('std'),
             't': InfoSetT(),
             'l': InfoSetL(),
             'tl': InfoSetTL()}


def load(file_name: str) -> tuple:
    info = file_name.split('/')[-1].split('.')[0].split('_')
    with open(file_name, 'rb') as file:
        strategy = pickle.load(file)
    return strategy, int(info[1]), models[info[2]], info_sets[info[3]]


def save(strategy: dict, trials: int, model: str, info_set: str) -> str:
    file_name = 'strategies/strat_{}_{}_{}.pickle'.format(trials, model, info_set)
    with open(file_name, 'wb') as file:
        pickle.dump(strategy, file)
    return file_name
