import argparse
import pickle
import time

from game.agent.regret_agent import RegretAgent
from game.figgie import Figgie
from game.model.simple_model import SimpleModel


def save(strategy: dict, trials: int, info_set_method: str) -> str:
    file_name = 'strategies/strategy_{}_{}.pickle'.format(trials, info_set_method)
    with open(file_name, 'wb') as file:
        pickle.dump(strategy, file)
    return file_name


def main():
    figgie = Figgie()
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, default=10_000, help='number of trials to run. ')
    parser.add_argument('-i', '--iterations', type=int, default=1, help='the number of times to train and run')
    args = parser.parse_args()

    agent = RegretAgent(SimpleModel())
    print('Parameters: ')
    print('\titerations: {}'.format(args.iterations))
    print('\ttrials: {}'.format(args.trials))
    print()

    for i in range(1, args.iterations + 1):
        print('Iteration: {}'.format(i))

        start_time = time.process_time()
        agent.train(figgie, args.trials)
        total_time = time.process_time() - start_time
        print('\tTraining took {} seconds '.format(total_time))

        print('\tStrategy: ')
        print('\t\tinfo sets: {}'.format(len(agent.game_tree)))

        start_time = time.process_time()
        file_name = save(agent.game_tree, args.trials * i, 'basic')
        total_time = time.process_time() - start_time
        print('\tSaving to {} took {} seconds'.format(file_name, total_time))


if __name__ == '__main__':
    main()