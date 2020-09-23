import argparse
import time

from game.agent.info_sets import *
from game.agent.modular_agent import RandomBuyPricer, RandomSellPricer
from game.model.simple_model import SimpleModel
from util import save


def main():
    figgie = Figgie()
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, default=10000, help='number of trials to run. ')

    args = parser.parse_args()
    info_sets = [InfoSetH(), InfoSetT(), InfoSetL(), InfoSetHT(), InfoSetHL(), InfoSetTL(), InfoSetHTL()]
    for info_set in info_sets:
        agent = RegretAgent(SimpleModel(), info_set, ModularAgent(SimpleModel(), RandomBuyPricer(), RandomSellPricer()))

        print('Parameters: ')
        print('\tinfo set: {}'.format(info_set.name))
        print('\tmodel: {}'.format('simple'))
        print('\ttrials: {}'.format(args.trials))
        print()

        start_time = time.process_time()
        agent.train(figgie, args.trials)
        total_time = time.process_time() - start_time
        print('\tTraining took {} seconds '.format(total_time))

        print('\tStrategy: ')
        print('\t\tinfo sets: {}'.format(len(agent.game_tree)))

        start_time = time.process_time()
        file_name = save(agent.game_tree, args.trials, 'simple', info_set.name)
        total_time = time.process_time() - start_time
        print('\tSaving to {} took {} seconds'.format(file_name, total_time))
        print('-----------------------------------')
        print()


if __name__ == '__main__':
    main()