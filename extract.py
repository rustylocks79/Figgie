import argparse

import numpy as np
from sklearn.linear_model import LinearRegression

from game.suit import Suit
from util import load


def dict_add(d, key, value):
    if key in d:
        d[key] += value
    else:
        d[key] = value


def main():
    #TODO: make a mathplotlib plot for each var verse best price. Adjust for htl
    parser = argparse.ArgumentParser(description='Extract info from strategy')
    parser.add_argument('-s', '--strategy', type=str, default='strategies/strat_10000_simple_std.pickle', help='the regret agent strategy')
    args = parser.parse_args()

    game_tree, trials, model, info_set = load(args.strategy)
    print('strategy at: {}'.format(args.strategy))
    print('\tnum info sets: {}'.format(len(game_tree)))
    print('\ttrials trained: {}'.format(trials))
    print('\tmodel: {}'.format(model.name))
    print('\tinfo set generator: {}'.format(info_set.name))

    count_asks = 0
    count_asks_empty = 0
    count_bids = 0
    count_bids_empty = 0

    asking_x = []
    asking_y = []
    asking_x_empty = []
    asking_y_empty = []
    bidding_x = []
    bidding_y = []
    bidding_x_empty = []
    bidding_y_empty = []


    for key in game_tree.keys():
        value = game_tree[key]
        strategy = value.get_trained_strategy()
        tokens = key.split(',')
        if tokens[0] == 'ask':
            card_util = int(tokens[1])
            selling_price = int(tokens[2]) if tokens[2] != 'N' else None
            hand = int(tokens[3])
            transactions = int(tokens[4])
            last_transaction = int(tokens[5]) if tokens[6] != 'N' else 0
            actions = info_set.generate_ask_actions(card_util, selling_price, Suit.CLUBS)
            best_action_index = strategy.argmax()
            best_action = actions[best_action_index]
            if selling_price is not None:
                count_asks += 1
                asking_x.append([selling_price, card_util, hand, transactions, last_transaction])
                asking_y.append(best_action.selling_price)
            else:
                count_asks_empty += 1
                asking_x_empty.append([card_util, hand, transactions, last_transaction])
                asking_y_empty.append(best_action.selling_price)
        elif tokens[0] == 'bid':
            card_util = int(tokens[1])
            buying_price = int(tokens[2]) if tokens[2] != 'N' else None
            hand = int(tokens[3])
            transactions = int(tokens[4])
            last_transaction = int(tokens[5]) if tokens[6] != 'N' else 0
            actions = info_set.generate_bid_actions(card_util, buying_price, Suit.CLUBS)
            best_action_index = strategy.argmax()
            best_action = actions[best_action_index]
            if buying_price is not None:
                count_bids += 1
                bidding_x.append([buying_price, card_util, hand, transactions, last_transaction])
                bidding_y.append(best_action.buying_price)
            else:
                count_bids_empty += 1
                bidding_x_empty.append([card_util, hand, transactions, last_transaction])
                bidding_y_empty.append(best_action.buying_price)
        elif tokens[0] == 'at':
            card_util = int(tokens[1])
            buying_price = int(tokens[2]) if tokens[2] != 'N' else None
            selling_price = int(tokens[3]) if tokens[3] != 'N' else None
            hand = int(tokens[4])
            transactions = int(tokens[5])
            last_transaction = int(tokens[6]) if tokens[6] != 'N' else 0
            actions = info_set.generate_at_actions(card_util, buying_price, selling_price, Suit.CLUBS)
            best_action_index = strategy.argmax()
            best_action = actions[best_action_index]
            if buying_price is not None:
                count_bids += 1
                bidding_x.append([buying_price, card_util, hand, transactions, last_transaction])
                bidding_y.append(best_action.buying_price)
            else:
                count_bids_empty += 1
                bidding_x_empty.append([card_util, hand, transactions, last_transaction])
                bidding_y_empty.append(best_action.buying_price)
            if selling_price is not None:
                count_asks += 1
                asking_x.append([selling_price, card_util, hand, transactions, last_transaction])
                asking_y.append(best_action.selling_price)
            else:
                count_asks_empty += 1
                asking_x_empty.append([card_util, hand, transactions, last_transaction])
                asking_y_empty.append(best_action.selling_price)

        else:
            raise ValueError('Invalid operation: {}'.format(key))

    print('\nResults\n')

    print('ask pricer: ')
    print('\tcount: {}'.format(count_asks))
    regression = LinearRegression()
    x = np.array(asking_x)
    y = np.array(asking_y)
    regression.fit(x, y)
    score = regression.score(x, y)
    print('\tscore: {}'.format(score))
    print('\tcoeff: {}'.format(regression.coef_))
    print('\tintercept: {}'.format(regression.intercept_))

    print('ask pricer in empty market: ')
    print('\tcount: {}'.format(count_asks_empty))
    regression = LinearRegression()
    x = np.array(asking_x_empty).reshape(-1, 1)
    y = np.array(asking_y_empty)
    regression.fit(x, y)
    score = regression.score(x, y)
    print('\tscore: {}'.format(score))
    print('\tcoeff: {}'.format(regression.coef_))
    print('\tintercept: {}'.format(regression.intercept_))

    print('bid pricer: ')
    print('\tcount: {}'.format(count_bids))
    regression = LinearRegression()
    x = np.array(bidding_x)
    y = np.array(bidding_y)
    regression.fit(x, y)
    score = regression.score(x, y)
    print('\tscore: {}'.format(score))
    print('\tcoeff: {}'.format(regression.coef_))
    print('\tintercept: {}'.format(regression.intercept_))

    print('bid pricer in empty market: ')
    print('\tcount: {}'.format(count_bids_empty))
    regression = LinearRegression()
    x = np.array(bidding_x_empty).reshape((-1, 1))
    y = np.array(bidding_y_empty)
    regression.fit(x, y)
    score = regression.score(x, y)
    print('\tscore: {}'.format(score))
    print('\tcoeff: {}'.format(regression.coef_))
    print('\tintercept: {}'.format(regression.intercept_))


if __name__ == '__main__':
    main()