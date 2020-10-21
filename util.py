import pickle

from agent.info_sets.info_set_h import InfoSetH
from agent.info_sets.info_set_l import InfoSetL
from agent.info_sets.info_set_o import InfoSetO
from agent.info_sets.info_set_std import InfoSetStd
from agent.info_sets.info_set_t import InfoSetT
from agent.models.cheating_model import CheatingModel
from agent.models.simple_model import SimpleModel

models = {
    'simple': SimpleModel(),
    'cheating': CheatingModel()
}

info_sets = {'std': InfoSetStd('std'),
             'h': InfoSetH(),
             't': InfoSetT(),
             'l': InfoSetL(),
             'o': InfoSetO()}


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
