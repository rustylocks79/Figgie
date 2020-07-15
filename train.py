import pickle
import time

from figgie import Figgie
from games import cfr

if __name__ == '__main__':
    TOTAL_TRIALS = 1_000_000
    game = Figgie()

    print('Using CFR to train Figgie with {} trials'.format(TOTAL_TRIALS))
    strategy, _ = cfr.train(game, TOTAL_TRIALS)
    print('Number of info sets: {} \n'.format(len(strategy)))

    print('Saving to file: ')
    start_time = time.process_time()
    with open('strategies/strategy.pickle', 'wb') as file:
        pickle.dump(strategy, file)
    total_time = time.process_time() - start_time
    print('Saving to file took {} \n'.format(total_time))