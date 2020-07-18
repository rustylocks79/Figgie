import pickle
import sys
import time
import argparse

from figgie import Figgie
import cfr
from isg import generate_info_set_basic


def save(strategy: dict, trials: int, info_set_method: str):
    file_name = 'strategies/strategy_{}_{}.pickle'.format(trials, info_set_method)
    print('Saving to {}: '.format(file_name))
    start_time = time.process_time()
    with open(file_name, 'wb') as file:
        pickle.dump(strategy, file)
    total_time = time.process_time() - start_time
    print('Saving to file took {} \n'.format(total_time))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, required=True, help='number of trials to run. ')
    args = parser.parse_args()
    game = Figgie()

    print('Using CFR to train Figgie with {} trials'.format(args.trials))
    strategy, _ = cfr.train(game, generate_info_set_basic, args.trials)

    print('Number of info sets: {}'.format(len(strategy)))
    print('Size of strategy in memory: {}\n'.format(sys.getsizeof(strategy)))

    save(strategy, args.trials, 'basic')
