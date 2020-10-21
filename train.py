import argparse
import time

import util
from agent.models.simple_model import SimpleModel
from agent.modular_agent import *
from agent.pricers.random_pricer import RandomPricer
from agent.regret_agent import RegretAgent
from figgie import Figgie
from util import load


def main():
    figgie = Figgie()
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, default=10_000, help='number of trials to run. ')
    parser.add_argument('-i', '--iterations', type=int, default=1, help='the number of times to train and run')
    parser.add_argument('-s', '--start', type=str, help='the strategy to start training')
    parser.add_argument('-g', '--generator', type=str, default='h', help="")
    args = parser.parse_args()

    if args.start is not None:
        game_tree, trials, model, info_set = load(args.start)
    else:
        game_tree = {}
        trials = 0
        info_set = util.info_sets[args.generator]

    agent = RegretAgent(SimpleModel(), info_set, ModularAgent(SimpleModel(), RandomPricer()), game_tree=game_tree)
    print('Parameters: ')
    print('\tinfo set: {}'.format(info_set.name))
    print('\tmodels: {}'.format('simple'))
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
        file_name = util.save(agent.game_tree, trials + args.trials * i, 'simple', info_set.name)
        total_time = time.process_time() - start_time
        print('\tSaving to {} took {} seconds'.format(file_name, total_time))


if __name__ == '__main__':
    main()