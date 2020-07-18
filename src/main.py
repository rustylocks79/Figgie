import pickle
import sys
import time
import argparse

from figgie import Figgie, SUITS
import cfr
from cfr import StrategyAgent, InfoSetGenerator
from game import RandomAgent


class ISGBasic(InfoSetGenerator):

    def __init__(self):
        super().__init__('basic')

    def generate(self, game) -> str:
        result = ''
        hand = game.cards[game.get_active_player()]
        for suit in SUITS:
            result += suit.to_abbr() + str(hand[suit.value])
        result += ':'
        for market in game.markets:
            result += market.suit.to_abbr()
            result += str(game.normalize_index(market.buying_player)) + str(
                market.buying_price) if market.buying_price is not None else 'NN'
            result += str(game.normalize_index(market.selling_player)) + str(
                market.selling_price) if market.selling_price is not None else 'NN'
        return result


class ISGAdvanced(InfoSetGenerator):

    def __init__(self):
        super().__init__('advanced')

    def generate(self, game) -> str:
        return super().generate(game)


def save(strategy: dict, trials: int, info_set_method: str):
    file_name = '../strategies/strategy_{}_{}.pickle'.format(trials, info_set_method)
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, default=10_000, help='number of trials to run. ')
    parser.add_argument('-g', '--games', type=int, default=10_000, help='number of test games to run. ')
    args = parser.parse_args()

    game = Figgie()
    isgb = ISGBasic()
    isga = ISGAdvanced()

    print('Using CFR to train Figgie. '.format(args.trials))
    print('\ttrials: {}'.format(args.trials))
    print('\tgenerator: {}'.format(isgb.name))
    start_time = time.process_time()
    strategy = cfr.train(game, isgb, args.trials)
    total_time = time.process_time() - start_time
    print('\ttime: {} seconds'.format(total_time))

    print('Strategy: ')
    print('\tinfo sets: {}'.format(len(strategy)))
    print('\tsize: {} bytes\n'.format(sys.getsizeof(strategy)))

    save(strategy, args.trials, 'basic')

    print('Playing {} games'.format(args.trials))
    start_time = time.process_time()
    agents = [RandomAgent(),
              RandomAgent(),
              RandomAgent(),
              StrategyAgent(strategy, isgb)]
    game.reset()
    game.play(agents, args.trials)
    total_time = time.process_time() - start_time
    print('\ttime: {} seconds'.format(total_time))

    for i in range(len(agents)):
        print('agent {}'.format(i))
        print('\twins: {}'.format(agents[i].wins))
        print('\ttotal utility: {}'.format(agents[i].total_utility))
        print('\tavg. utility: {}'.format(agents[i].total_utility / args.trials))
        if isinstance(agents[i], StrategyAgent):
            print('\tunknown states: {}'.format(agents[i].unknown_states))
            print('\tavg unknown states: {}'.format(agents[i].unknown_states / args.trials))
