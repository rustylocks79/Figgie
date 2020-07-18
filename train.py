import pickle
import sys
import time
import argparse

from figgie import Figgie, SUITS
from games import cfr


def save(strategy: map, trials: int, info_set_method: str):
    file_name = 'strategies/strategy_{}_{}.pickle'.format(trials, info_set_method)
    print('Saving to {}: '.format(file_name))
    start_time = time.process_time()
    with open(file_name, 'wb') as file:
        pickle.dump(strategy, file)
    total_time = time.process_time() - start_time
    print('Saving to file took {} \n'.format(total_time))


def generate_info_set_basic(figgie):
    result = ''
    hand = game.cards[figgie.get_active_player()]
    for suit in SUITS:
        result += suit.to_abbr() + str(hand[suit.value])
    result += ':'
    for market in figgie.markets:
        result += market.suit.to_abbr()
        result += str(figgie.normalize_index(market.buying_player)) + str(
            market.buying_price) if market.buying_price is not None else 'NN'
        result += str(figgie.normalize_index(market.selling_player)) + str(
            market.selling_price) if market.selling_price is not None else 'NN'
    return result


def generate_info_set_advanced(figgie):
    pass


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
