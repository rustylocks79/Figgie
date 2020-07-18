import argparse
import pickle
import time

from figgie import Figgie
from game import StrategyAgent
from isg import generate_info_set_basic


def load(file_name: str) -> dict:
    print('Loading from file: ')
    start_time = time.process_time()
    with open(file_name, 'rb') as file:
        strategy = pickle.load(file)
    total_time = time.process_time() - start_time
    print('Loading from file took {} \n'.format(total_time))
    return strategy


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Testing a strategy')
    parser.add_argument('-t', '--trials', type=int, required=True, help='number of trials to run. ')
    parser.add_argument('-s', '--strategy', type=str, required=True, help='the strategy to test')
    args = parser.parse_args()
    game = Figgie()

    strategy = load(args.strategy)

    print('Found strategy with {} states \n'.format(len(strategy)))

    print('Playing {} games'.format(args.trials))
    start_time = time.process_time()
    agents = [StrategyAgent(strategy, generate_info_set_basic),
              StrategyAgent(strategy, generate_info_set_basic),
              StrategyAgent(strategy, generate_info_set_basic),
              StrategyAgent(strategy, generate_info_set_basic)]
    game.reset()
    game.play(agents, args.trials)
    total_time = time.process_time() - start_time
    print('Playing Took {}'.format(total_time))

    for i in range(len(agents)):
        print('agent {}'.format(i))
        print('\twins: {}'.format(agents[i].wins))
        print('\ttotal utility: {}'.format(agents[i].total_utility))
        print('\tavg. utility: {}'.format(agents[i].total_utility / args.trials))
        if isinstance(agents[i], StrategyAgent):
            print('\tunknown states: {}'.format(agents[i].unknown_states))
            print('\tavg unknown states: {}'.format(agents[i].unknown_states / args.trials))
