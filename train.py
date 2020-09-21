import argparse
import pickle
import time

from game.agent.info_sets import InfoSetH, InfoSetT, InfoSetL, InfoSetHT, InfoSetHL, InfoSetTL, InfoSetHTL
from game.agent.modular_agent import *
from game.agent.regret_agent import RegretAgent
from game.figgie import Figgie
from game.model.simple_model import SimpleModel


def save(strategy: dict, trials: int, model: str) -> str:
    file_name = 'strategies/strategy_{}_{}.pickle'.format(trials, model)
    with open(file_name, 'wb') as file:
        pickle.dump(strategy, file)
    return file_name


def load(file_name: str) -> dict:
    with open(file_name, 'rb') as file:
        strategy = pickle.load(file)
    return strategy


def main():
    info_sets = {'h': InfoSetH(),
                 't': InfoSetT(),
                 'l': InfoSetL(),
                 'ht': InfoSetHT(),
                 'hl': InfoSetHL(),
                 'tl': InfoSetTL(),
                 'htl': InfoSetHTL()}

    figgie = Figgie()
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, default=10_000, help='number of trials to run. ')
    parser.add_argument('-i', '--iterations', type=int, default=1, help='the number of times to train and run')
    parser.add_argument('-s', '--start', type=str, help='the strategy to start training')
    parser.add_argument('-g', '--generator', type=str, default='h', help="")
    args = parser.parse_args()

    if args.start is not None:
        game_tree = load(args.start)
    else:
        game_tree = {}

    if args.generator in info_sets:
        info_set = info_sets[args.generator]
    else:
        raise ValueError('Unknown info set generator: {}'.format(args.info))

    agent = RegretAgent(SimpleModel(), info_set, ModularAgent(SimpleModel(), RandomBuyPricer(), RandomSellPricer()), game_tree=game_tree)
    print('Parameters: ')
    print('\tinfo set: {}'.format(info_set.name))
    print('\tmodel: {}'.format('simple'))
    print('\titerations: {}'.format(args.iterations))
    print('\ttrials: {}'.format(args.trials))
    print()

    # TODO: add initial trials

    for i in range(1, args.iterations + 1):
        print('Iteration: {}'.format(i))

        start_time = time.process_time()
        agent.train(figgie, args.trials)
        total_time = time.process_time() - start_time
        print('\tTraining took {} seconds '.format(total_time))

        print('\tStrategy: ')
        print('\t\tinfo sets: {}'.format(len(agent.game_tree)))

        start_time = time.process_time()
        file_name = save(agent.game_tree, args.trials * i, 'simple_{}'.format(args.generator))
        total_time = time.process_time() - start_time
        print('\tSaving to {} took {} seconds'.format(file_name, total_time))


if __name__ == '__main__':
    main()