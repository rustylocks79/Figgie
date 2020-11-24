import argparse

import matplotlib.pyplot as plt
import numpy as np
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor

from agent.info_sets.info_set_std import InfoSetStd
from figgie import Suit
from prog import load


def dict_add(d, key, value):
    if key in d:
        d[key] += value
    else:
        d[key] = value


def main():
    parser = argparse.ArgumentParser(description='Extract info from strategy')
    parser.add_argument('-s', '--strategy', type=str, default='strategies/strat_1000000_simple_std.pickle', help='the regret agent strategy')
    args = parser.parse_args()

    # TODO: dynamic
    info_set = InfoSetStd('std')

    game_tree, trials = load(args.strategy)
    print('strategy at: {}'.format(args.strategy))
    print('\tnum info sets: {}'.format(len(game_tree)))
    print('\ttrials trained: {}'.format(trials))
    # print('\tmodels: {}'.format(model.name))
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
        card_util = int(tokens[1])
        if tokens[0] == 'ask':
            selling_price = int(tokens[2]) if tokens[2] != 'N' else None
            actions = info_set.generate_ask_actions(card_util, selling_price, Suit.CLUBS)
            best_price = actions[strategy.argmax()]
            if selling_price is not None:
                count_asks += 1
                asking_x.append([selling_price, card_util])
                asking_y.append(best_price)
            else:
                count_asks_empty += 1
                asking_x_empty.append(card_util)
                asking_y_empty.append(best_price)
        elif tokens[0] == 'bid':
            buying_price = int(tokens[2]) if tokens[2] != 'N' else None
            actions = info_set.generate_bid_actions(card_util, buying_price, Suit.CLUBS)
            best_price = actions[strategy.argmax()]
            if buying_price is not None:
                count_bids += 1
                bidding_x.append([buying_price, card_util])
                bidding_y.append(best_price)
            else:
                count_bids_empty += 1
                bidding_x_empty.append(card_util)
                bidding_y_empty.append(best_price)
        elif tokens[0] == 'at':
            buying_price = int(tokens[2]) if tokens[2] != 'N' else None
            selling_price = int(tokens[3]) if tokens[3] != 'N' else None
            actions = info_set.generate_at_actions(card_util, buying_price, selling_price, Suit.CLUBS)
            best_price = actions[strategy.argmax()]
            if buying_price is not None:
                count_bids += 1
                bidding_x.append([buying_price, card_util])
                bidding_y.append(best_price[0])
            else:
                count_bids_empty += 1
                bidding_x_empty.append(card_util)
                bidding_y_empty.append(best_price[0])

            if selling_price is not None:
                count_asks += 1
                asking_x.append([selling_price, card_util])
                asking_y.append(best_price[1])
            else:
                count_asks_empty += 1
                asking_x_empty.append(card_util)
                asking_y_empty.append(best_price[1])

        else:
            raise ValueError('Invalid operation: {}'.format(key))

    print('\nResults\n')

    print('ask pricer: ')
    print('\tcount: {}'.format(count_asks))
    regression = DecisionTreeRegressor(max_depth=5)
    x = np.array(asking_x)
    y = np.array(asking_y, dtype=np.int32)
    regression.fit(x, y)
    fig = plt.figure(figsize=(25, 20))
    tree.plot_tree(regression)
    # fig.show()
    fig.savefig('asking_tree.png')
    # score = regression.score(x, y)
    # print('\tscore: {}'.format(score))
    # print('\tcoeff: {}'.format(regression.coef_))
    # print('\tintercept: {}'.format(regression.intercept_))

    # print('ask pricer in empty market: ')
    # print('\tcount: {}'.format(count_asks_empty))
    # regression = DecisionTreeClassifier()
    # x = np.array(asking_x_empty).reshape(-1, 1)
    # y = np.array(asking_y_empty, dtype=np.int32)
    # regression.fit(x, y)
    # tree.plot_tree(regression)
    # score = regression.score(x, y)
    # print('\tscore: {}'.format(score))
    # print('\tcoeff: {}'.format(regression.coef_))
    # print('\tintercept: {}'.format(regression.intercept_))

    # print('bid pricer: ')
    # print('\tcount: {}'.format(count_bids))
    # regression = LinearRegression()
    # x = np.array(bidding_x)
    # y = np.array(bidding_y, dtype=np.int32)
    # regression.fit(x, y)
    # tree.plot_tree(regression)
    # score = regression.score(x, y)
    # print('\tscore: {}'.format(score))
    # print('\tcoeff: {}'.format(regression.coef_))
    # print('\tintercept: {}'.format(regression.intercept_))

    # print('bid pricer in empty market: ')
    # print('\tcount: {}'.format(count_bids_empty))
    # regression = LinearRegression()
    # x = np.array(bidding_x_empty).reshape(-1, 1)
    # y = np.array(bidding_y_empty, dtype=np.int32)
    # regression.fit(x, y)
    # tree.plot_tree(regression)
    # score = regression.score(x, y)
    # print('\tscore: {}'.format(score))
    # print('\tcoeff: {}'.format(regression.coef_))
    # print('\tintercept: {}'.format(regression.intercept_))


if __name__ == '__main__':
    main()