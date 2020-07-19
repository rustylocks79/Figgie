import argparse
import pickle
import sys
import time

from cfr import CFRMinimizer
from agents import RandomAgent, StrategyAgent
from figgie import Figgie
from generators import isg_basic, isg_abstract, ag_basic, ag_abstract, am_abstract


def save(strategy: dict, trials: int, info_set_method: str):
    file_name = 'strategies/strategy_{}_{}.pickle'.format(trials, info_set_method)
    print('Saving to {}: '.format(file_name))
    start_time = time.process_time()
    with open(file_name, 'wb') as file:
        pickle.dump(strategy, file)
    total_time = time.process_time() - start_time
    print('Saving to file took {} \n'.format(total_time))


def load(file_name: str) -> dict:
    print('Loading from file: ')
    start_time = time.process_time()
    with open(file_name, 'rb') as file:
        strategy = pickle.load(file)
    total_time = time.process_time() - start_time
    print('Loading from file took {} \n'.format(total_time))
    return strategy


def play(game: Figgie, agents: list, games: int):
    print('Testing: ')
    game.reset()
    start_time = time.process_time()
    game.play(agents, games)
    total_time = time.process_time() - start_time
    print('\ttime: {} seconds'.format(total_time))

    print('Results: ')
    for i, agent in enumerate(agents):
        print('agent {}'.format(i))
        print('\tag: {}'.format(agent.action_generator.__name__))
        if agent.action_mapper is not None:
            print('\tam: {}'.format(agent.action_mapper.__name__))
        print('\twins: {}'.format(agent.wins))
        print('\ttotal utility: {}'.format(agent.total_utility))
        print('\tavg. utility: {}'.format(agent.total_utility / games))
        if isinstance(agent, StrategyAgent):
            print('\tisg: {}'.format(agent.info_set_generator.__name__))
            print('\tunknown states: {}'.format(agent.unknown_states))
            print('\tavg unknown states: {}'.format(agent.unknown_states / games))


def main():
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, default=10_000, help='number of trials to run. ')
    parser.add_argument('-i', '--iterations', type=int, default=1, help='the number of times to train and run')
    parser.add_argument('-g', '--games', type=int, default=10_000, help='number of test games to run. ')
    args = parser.parse_args()

    game = Figgie()
    minimizer = CFRMinimizer(game, isg_basic, ag_abstract, am_abstract)
    print('Parameters: ')
    print('\titerations: {}'.format(args.iterations))
    print('\ttrials: {}'.format(args.trials))
    print('\tgames: {}'.format(args.games))
    print('\tinfo set generator: {}'.format(minimizer.info_set_generator.__name__))
    print('\taction generator: {}'.format(minimizer.action_generator.__name__))
    print('\tinfo set generator: {}'.format(minimizer.action_mapper.__name__))
    print()

    for i in range(args.iterations):
        print('Training: ')
        start_time = time.process_time()
        minimizer.train(args.trials)
        strategy = minimizer.get_strategy()
        total_time = time.process_time() - start_time
        print('\ttime: {} seconds'.format(total_time))

        print('Strategy: ')
        print('\tinfo sets: {}'.format(len(strategy)))
        print('\tsize: {} bytes\n'.format(sys.getsizeof(strategy)))

        save(strategy, args.trials * (i + 1), 'basic')

        agents = [RandomAgent(ag_basic),
                  RandomAgent(ag_basic),
                  RandomAgent(ag_basic),
                  StrategyAgent(strategy, isg_basic, ag_abstract, am_abstract)]

        play(game, agents, args.games)


if __name__ == '__main__':
    main()
