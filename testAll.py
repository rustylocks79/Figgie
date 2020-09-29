import argparse
import os

import test
from game.agent.modular_agent import *
from game.agent.regret_agent import RegretAgent
from game.figgie import Figgie
from game.model.simple_model import SimpleModel
from util import load


def main():
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, default=10_000, help='number of tests games to run. ')
    args = parser.parse_args()
    print('Parameters: ')
    print('\ttrials: {}'.format(args.trials))
    print()
    print('----------------------------------------------------------------------------------------------')

    path = 'strategies/'
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            figgie = Figgie()

            game_tree, trials, model, info_set = load(file_path)
            print('Found strategy at: {}'.format(file_path))
            print('\tnum info sets: {}'.format(len(game_tree)))
            print('\ttrials trained: {}'.format(trials))
            print('\tmodel: {}'.format(model.name))
            print('\tinfo set generator: {}'.format(info_set.name))

            agents = [ModularAgent(SimpleModel(), MarketBuyPricer(), MarketSellPricer()),
                      ModularAgent(SimpleModel(), UtilBuyPricer(), UtilSellPricer()),
                      ModularAgent(SimpleModel(), RandomBuyPricer(), RandomSellPricer()),
                      RegretAgent(model, info_set, ModularAgent(SimpleModel(), HalfBuyPricer(), HalfSellPricer()),
                                  game_tree=game_tree)]

            test.test(figgie, agents, args.trials, False)
            print('----------------------------------------------------------------------------------------------')


if __name__ == '__main__':
    main()