import argparse
import pickle
import sys
import time

from api.cfr import CFRMinimizer
from api.agent import RandomAgent, StrategyAgent
from games.figgie import Figgie
from games.generators import isg_abstract, ag_basic, ag_abstract, am_abstract


def save(strategy: dict, trials: int, info_set_method: str) -> str:
    file_name = 'strategies/strategy_{}_{}.pickle'.format(trials, info_set_method)
    with open(file_name, 'wb') as file:
        pickle.dump(strategy, file)
    return file_name


def load(file_name: str) -> dict:
    with open(file_name, 'rb') as file:
        strategy = pickle.load(file)
    return strategy


def play(game: Figgie, agents: list, games: int):
    game.reset()
    start_time = time.process_time()
    game.play(agents, games)
    total_time = time.process_time() - start_time
    print('\tTesting took {} seconds'.format(total_time))

    print('\tResults: ')
    for i, agent in enumerate(agents):
        print('\tagent {}'.format(i))
        print('\t\twins: {}'.format(agent.wins))
        print('\t\tavg. utility: {}, total utility: {}'.format(agent.total_utility / games, agent.total_utility))
        if isinstance(agent, StrategyAgent):
            print('\t\tavg unknown states: {}, unknown states: {}'.format(agent.unknown_states / games, agent.unknown_states))


def main():
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, default=10_000, help='number of trials to run. ')
    parser.add_argument('-i', '--iterations', type=int, default=1, help='the number of times to train and run')
    parser.add_argument('-g', '--games', type=int, default=10_000, help='number of test games to run. ')
    args = parser.parse_args()

    game = Figgie()
    minimizer = CFRMinimizer(game, isg_abstract, ag_abstract, am_abstract)
    print('Parameters: ')
    print('\titerations: {}'.format(args.iterations))
    print('\ttrials: {}'.format(args.trials))
    print('\tgames: {}'.format(args.games))
    print('\tinfo set generator: {}'.format(minimizer.info_set_generator.__name__))
    print('\taction generator: {}'.format(minimizer.action_generator.__name__))
    print('\tinfo set generator: {}'.format(minimizer.action_mapper.__name__))
    print()

    # for i, agent in enumerate(agents):
    #     print('agent {} ({})'.format(i, type(agent)))
    #     if isinstance(agent, StrategyAgent):
    #         print('\tisg: {}'.format(agent.info_set_generator.__name__))
    #     print('\tag: {}'.format(agent.action_generator.__name__))
    #     if agent.action_mapper is not None:
    #         print('\tam: {}'.format(agent.action_mapper.__name__))
    # print()

    for i in range(1, args.iterations + 1):
        print('Iteration: {}'.format(i))

        start_time = time.process_time()
        minimizer.train(args.trials)
        total_time = time.process_time() - start_time
        print('\tTraining took {} seconds '.format(total_time))

        start_time = time.process_time()
        strategy = minimizer.get_strategy()
        total_time = time.process_time() - start_time
        print('\tExtracting took {} seconds'.format(total_time))

        print('\tStrategy: ')
        print('\t\tinfo sets: {}'.format(len(strategy)))
        print('\t\tsize: {} bytes'.format(sys.getsizeof(strategy)))

        start_time = time.process_time()
        file_name = save(strategy, args.trials * i, 'basic')
        total_time = time.process_time() - start_time
        print('\tSaving to {} took {} seconds'.format(file_name, total_time))

        agents = [RandomAgent(ag_basic),
                  RandomAgent(ag_basic),
                  RandomAgent(ag_basic),
                  StrategyAgent(strategy, isg_abstract, ag_abstract, am_abstract)]
        play(game, agents, args.games)

        print('---------------------------------------------------')


if __name__ == '__main__':
    main()
