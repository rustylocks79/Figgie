import argparse
import time

from game.agent.modular_agent import *
from game.agent.regret_agent import RegretAgent
from game.figgie import Figgie
from game.model.simple_model import SimpleModel
from util import load


def test(game: Figgie, agents: list, games: int, verbose=False):
    start_time = time.process_time()
    game.play(agents, games, verbose=verbose)
    total_time = time.process_time() - start_time
    print('Testing took {} seconds'.format(total_time))

    print('Results: ')
    for i, agent in enumerate(agents):
        print('agent {}: ({})'.format(i, type(agent)))
        print('\twins: {}'.format(agent.wins))
        print('\tavg. utility: {}, total utility: {}'.format(agent.total_utility / games, agent.total_utility))
        print('\trmse of model: {}'.format(agent.get_rmse()))
        print('\toperations: {}'.format({key: agent.operations[key] for key in sorted(agent.operations)}))
        percentOperations = agent.get_operation_percents()
        print('\tpercent operations: {}'.format({key: percentOperations[key] for key in sorted(percentOperations)}))
        if isinstance(agent, RegretAgent):
            print('\tavg unknown states: {}, unknown states: {}'.format(agent.unknown_states / games, agent.unknown_states))


def main():
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, default=10_000, help='number of tests games to run. ')
    parser.add_argument('-v', '--verbose', type=bool, default=False, help='output actions')
    parser.add_argument('-s', '--strategy', type=str, default='strategies/strategy_10000_simple.pickle', help='the regret agent strategy')
    args = parser.parse_args()

    figgie = Figgie()
    print('Parameters: ')
    print('\ttrials: {}'.format(args.trials))
    print('\tverbose: {}'.format(args.verbose))
    print('\tstrategy: {}'.format(args.strategy))
    game_tree, trials, model, info_set = load(args.strategy)
    print('\t\tnum info sets: {}'.format(len(game_tree)))
    print('\t\ttrials trained: {}'.format(trials))
    print('\t\tmodel: {}'.format(model))
    print('\t\tinfo set generator: {}'.format(info_set.name))

    agents = [ModularAgent(SimpleModel(), MarketBuyPricer(), MarketSellPricer()),
              ModularAgent(SimpleModel(), UtilBuyPricer(), UtilSellPricer()),
              ModularAgent(SimpleModel(), RandomBuyPricer(), RandomSellPricer()),
              RegretAgent(model, info_set, ModularAgent(SimpleModel(), HalfBuyPricer(), HalfSellPricer()), game_tree=game_tree)]

    test(figgie, agents, args.trials, args.verbose)


if __name__ == '__main__':
    main()
