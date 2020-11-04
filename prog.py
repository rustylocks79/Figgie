import argparse
import json
import pickle
import time
from statistics import median

from agent.choosers.simple_chooser import SimpleChooser
from agent.info_sets.info_set_h import InfoSetH
from agent.info_sets.info_set_l import InfoSetL
from agent.info_sets.info_set_o import InfoSetO
from agent.info_sets.info_set_std import InfoSetStd
from agent.info_sets.info_set_t import InfoSetT
from agent.models.ann_model import AnnModel
from agent.models.simple_model import SimpleModel
from agent.models.utility_model import UtilityModel
from agent.modular_agent import ModularAgent
from agent.pricers.faded_pricer import FadedPricer
from agent.pricers.half_pricer import HalfPricer
from agent.pricers.random_pricer import RandomPricer
from agent.regret_agent import RegretAgent, InfoSetGenerator
from figgie import Figgie


def load(file_name: str) -> tuple:
    info = file_name.split('/')[-1].split('.')[0].split('_')
    with open(file_name, 'rb') as file:
        strategy = pickle.load(file)
    return strategy, int(info[1])


def save(strategy: dict, trials: int, model: str, info_set: str) -> str:
    file_name = 'strategies/strat_{}_{}_{}.pickle'.format(trials, model, info_set)
    with open(file_name, 'wb') as file:
        pickle.dump(strategy, file)
    return file_name


info_sets = {'std': InfoSetStd('std'),
             'h': InfoSetH(),
             't': InfoSetT(),
             'l': InfoSetL(),
             'o': InfoSetO()}

pricers = {'half': HalfPricer(),
           'random': RandomPricer(),
           "faded": FadedPricer()}


def get_model(parameters: dict) -> UtilityModel:
    model = parameters['model']
    if model == 'simple':
        return SimpleModel()
    elif model == 'ann':
        path = parameters['model_path']
        return AnnModel(path)
    else:
        raise ValueError('Invalid model: {}'.format(model))


def load_agents(parameters: dict) -> list:
    agents = []
    for agent_dict in parameters['agents']:
        agent_type = agent_dict['type']
        model = get_model(agent_dict)
        if 'collect' in agent_dict:
            collect = agent_dict['collect'] == 'True'
        else:
            collect = False
        if agent_type == 'modular':
            pricer = pricers[agent_dict['pricer']]
            agents.append(ModularAgent(model, SimpleChooser(), pricer))
        elif agent_type == 'regret':
            info_set = info_sets[agent_dict['info_set']]
            strategy, trails = load(agent_dict['strategy'])
            agents.append(RegretAgent(model, SimpleChooser(), info_set, ModularAgent(model, SimpleChooser(), RandomPricer()), strategy, collector=collect))
    return agents


def train(iterations: int, trials: int, prev_trials: int, info_set: InfoSetGenerator, model: UtilityModel, game_tree):
    agent = RegretAgent(model, SimpleChooser(), info_set,
                        ModularAgent(model, SimpleChooser(), RandomPricer()), game_tree=game_tree)
    figgie = Figgie()
    for i in range(1, iterations + 1):
        print('Iteration: {}'.format(i))

        start_time = time.process_time()
        agent.train(figgie, trials)
        total_time = time.process_time() - start_time
        print('\tTraining took {} seconds '.format(total_time))

        print('\tStrategy: ')
        print('\t\tinfo sets: {}'.format(len(agent.game_tree)))

        observations = [x.observations for x in agent.game_tree.values()]
        mean = sum(observations) / len(observations)
        variance = sum([((x - mean) ** 2) for x in observations]) / len(observations)
        dev = variance ** 0.5

        print('\t\tavg operations: {}'.format(mean))
        print('\t\tmedian operations: {}'.format(median(observations)))
        print('\t\tstd dev. operations: {}'.format(dev))

        start_time = time.process_time()
        file_name = save(agent.game_tree, prev_trials + trials * i, 'simple', info_set.name)
        total_time = time.process_time() - start_time
        print('\tSaving to {} took {} seconds'.format(file_name, total_time))


def test(agents: list, trials: int, verbose=False):
    figgie = Figgie()
    start_time = time.process_time()
    figgie.play(agents, trials, verbose=verbose)
    total_time = time.process_time() - start_time
    print('Testing took {} seconds'.format(total_time))

    print('Results: ')
    for i, agent in enumerate(agents):
        print('agent {}: ({})'.format(i, agent.name))
        print('\twins: {}'.format(agent.wins))
        print('\tavg. utility: {}, total utility: {}'.format(agent.total_utility / trials, agent.total_utility))
        print('\toperations: {}'.format({key: agent.operations[key] for key in sorted(agent.operations)}))
        avg_operations = agent.get_avg_operations(trials)
        print('\tavg. operations: {}'.format({key: avg_operations[key] for key in sorted(avg_operations)}))
        if isinstance(agent, RegretAgent):
            print('\tavg unknown states: {}, unknown states: {}'.format(agent.unknown_states / trials, agent.unknown_states))

    for agent in agents:
        if agent.collector:
            with open('ann/training_data.pickle', 'wb') as file:
                pickle.dump(agent.training_data, file)


def main():
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-in', '--input', type=str, help='a json input file with necessary parameters')
    args = parser.parse_args()
    with open(args.input, 'r') as file:
        parameters = json.load(file)
    if parameters['mode'] == 'train':
        iterations = parameters['iterations']
        trials = parameters['trials']
        info_set = info_sets[parameters['info_set']]
        model = get_model(parameters)
        if 'start' in parameters:
            start, prev_trials = load(parameters['start'])
        else:
            start = {}
            prev_trials = 0
            
        print('Parameters')
        print('\titerations: {}'.format(iterations))
        print('\ttrials: {}'.format(trials))
        print('\tprev_trials: {}'.format(prev_trials))
        print('\tinfo_set: {}'.format(info_set.name))
        print('\tmodel: {}'.format(model.name))
        train(iterations, trials, prev_trials, info_set, model, start)
    elif parameters['mode'] == 'test':
        trials = parameters['trials']
        agents = load_agents(parameters)
        verbose = parameters['verbose'] == 'True'
        print('Parameters')
        print('\ttrials: {}'.format(trials))
        print('\tverbose: {}'.format(verbose))
        test(agents, trials, verbose)
    else:
        raise ValueError('Invalid Mode: {}'.format(parameters['mode']))


if __name__ == '__main__':
    main()