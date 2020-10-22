import argparse
import pickle
import time

from agent.info_sets.info_set_std import InfoSetStd
from agent.models.ann_model import AnnModel
from agent.models.simple_model import SimpleModel
from agent.modular_agent import *
from agent.pricers.faded_pricer import FadedPricer
from agent.pricers.half_pricer import HalfPricer
from agent.pricers.random_pricer import RandomPricer
from agent.regret_agent import RegretAgent
from figgie import Figgie
from util import load


def test(game: Figgie, agents: list, trials: int, verbose=False):
    start_time = time.process_time()
    game.play(agents, trials, verbose=verbose)
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


def main():
    parser = argparse.ArgumentParser(description='Test a strategy')
    parser.add_argument('-t', '--trials', type=int, default=10_000, help='number of tests games to run. ')
    parser.add_argument('-v', '--verbose', type=bool, default=False, help='output actions')
    parser.add_argument('-s', '--strategy', type=str, default='strategies/strat_10000_simple_std.pickle', help='the regret agent strategy')
    parser.add_argument('-m', '--mode', type=str, default='m', help='r for regret opponents, m for modular opponents. ')
    parser.add_argument('-c', '--collect', type=bool, default=False)
    args = parser.parse_args()

    figgie = Figgie()
    print('Parameters: ')
    print('\ttrials: {}'.format(args.trials))
    print('\tverbose: {}'.format(args.verbose))
    print('\tstrategy: {}'.format(args.strategy))
    print('\tcollect: {}'.format(args.collect))
    game_tree, trials, model, info_set = load(args.strategy)
    print('\t\tnum info sets: {}'.format(len(game_tree)))
    print('\t\ttrials trained: {}'.format(trials))
    print('\t\tmodels: {}'.format(model.name))
    print('\t\tinfo set generator: {}'.format(info_set.name))

    if args.mode == 'm':
        agents = [ModularAgent(SimpleModel(), SimpleChooser(), HalfPricer()),
                  ModularAgent(SimpleModel(), SimpleChooser(), RandomPricer()),
                  ModularAgent(AnnModel(), SimpleChooser(), FadedPricer()),
                  RegretAgent(model, SimpleChooser(), info_set, ModularAgent(SimpleModel(), SimpleChooser(), RandomPricer()), game_tree=game_tree, collector=args.collect)]
    else:
        std_game_tree, _, _, _ = load('strategies/strat_1000000_simple_std.pickle')
        agents = [RegretAgent(SimpleModel(), SimpleChooser(), InfoSetStd('std'), ModularAgent(SimpleModel(), SimpleChooser(), HalfPricer()), game_tree=std_game_tree),
                  RegretAgent(SimpleModel(), SimpleChooser(), InfoSetStd('std'), ModularAgent(SimpleModel(), SimpleChooser(), HalfPricer()), game_tree=std_game_tree),
                  RegretAgent(SimpleModel(), SimpleChooser(), InfoSetStd('std'), ModularAgent(SimpleModel(), SimpleChooser(), HalfPricer()), game_tree=std_game_tree),
                  RegretAgent(model, SimpleChooser(), info_set, ModularAgent(SimpleModel(),  SimpleChooser(), HalfPricer()), game_tree=game_tree, collector=args.collect)]

    test(figgie, agents, args.trials, args.verbose)

    if args.collect:
        with open('ann/training_data.pickle', 'wb') as file:
            pickle.dump(agents[3].training_data, file)


if __name__ == '__main__':
    main()
