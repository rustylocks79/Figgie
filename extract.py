import argparse

import matplotlib.pyplot as plt
import numpy as np
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor

from agent.info_sets.info_set_std import InfoSetStd
from agent.pricers.half_pricer import HalfPricer
from figgie import Suit
from prog import load

prefix = 'new_'

def dict_add(d, key, value):
    if key in d:
        d[key] += value
    else:
        d[key] = value


def main():
    parser = argparse.ArgumentParser(description='Extract info from strategy')
    parser.add_argument('-s', '--strategy', type=str, help='the regret agent strategy')
    args = parser.parse_args()

    info_set = InfoSetStd('std')
    half_pricer = HalfPricer()

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
    asking_x_empty = []
    asking_y = []
    asking_y_empty = []

    bidding_x = []
    bidding_x_empty = []
    bidding_y = []
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
            half_price = half_pricer.get_asking_price_internal(selling_price, card_util)
            if best_price <= 100:
                if selling_price is not None:
                    count_asks += 1
                    asking_x.append([selling_price, card_util])
                    asking_y.append(best_price - half_price)
                else:
                    count_asks_empty += 1
                    asking_x_empty.append(card_util)
                    asking_y_empty.append(best_price)
        elif tokens[0] == 'bid':
            buying_price = int(tokens[2]) if tokens[2] != 'N' else None
            actions = info_set.generate_bid_actions(card_util, buying_price, Suit.CLUBS)
            best_price = actions[strategy.argmax()]
            half_price = half_pricer.get_bidding_price_internal(buying_price, card_util)
            if best_price <= 100:
                if buying_price is not None:
                    count_bids += 1
                    bidding_x.append([buying_price, card_util])
                    bidding_y.append(best_price - half_price)
                else:
                    count_bids_empty += 1
                    bidding_x_empty.append(card_util)
                    bidding_y_empty.append(best_price)
        else:
            buying_price = int(tokens[2]) if tokens[2] != 'N' else None
            selling_price = int(tokens[3]) if tokens[3] != 'N' else None
            actions = info_set.generate_at_actions(card_util, buying_price, selling_price, Suit.CLUBS)
            best_price = actions[strategy.argmax()]
            half_price = half_pricer.get_at_price_internal(buying_price, selling_price, card_util)
            if best_price[0] <= 100:
                if buying_price is not None:
                    count_bids += 1
                    bidding_x.append([buying_price, card_util])
                    bidding_y.append(best_price[0] - half_price[0])
                else:
                    count_bids_empty += 1
                    bidding_x_empty.append(card_util)
                    bidding_y_empty.append(best_price[0])

            if best_price[1] <= 100:
                if selling_price is not None:
                    count_asks += 1
                    asking_x.append([selling_price, card_util])
                    asking_y.append(best_price[1] - half_price[1])
                else:
                    count_asks_empty += 1
                    asking_x_empty.append(card_util)
                    asking_y_empty.append(best_price[1])

    print('\nResults\n')

    print(prefix + 'ask pricer: ')
    print('\tcount: {}'.format(count_asks))
    regression = DecisionTreeRegressor(max_depth=3)
    x = np.array(asking_x, dtype=(np.float32, np.float32))
    y = np.array(asking_y, dtype=np.float64)
    regression.fit(x, y)

    fig = plt.figure(figsize=(16, 10))
    tree.plot_tree(regression, feature_names=['market price', 'model util'], filled=True, fontsize=10)
    fig.savefig('asking_tree.png')

    # print(prefix + 'asking empty pricer: ')
    # print('\tcount: {}'.format(count_asks))
    # regression = DecisionTreeRegressor(max_depth=3)
    # x = np.array(asking_x_empty, dtype=np.float32)
    # y = np.array(asking_y_empty, dtype=np.float64)
    # x = x.reshape(-1, 1)
    # regression.fit(x, y)
    #
    # fig = plt.figure(figsize=(16, 10))
    # tree.plot_tree(regression, feature_names=['model util'], filled=True, fontsize=10)
    # fig.savefig('asking_tree_empty.png')

    # print(prefix + 'bidding pricer: ')
    # print('\tcount: {}'.format(count_asks))
    # regression = DecisionTreeRegressor(max_depth=3)
    # x = np.array(bidding_x, dtype=(np.float32, np.float32))
    # y = np.array(bidding_y, dtype=np.float64)
    # regression.fit(x, y)
    #
    # fig = plt.figure(figsize=(16, 10))
    # tree.plot_tree(regression, feature_names=['market price', 'model util'], filled=True, fontsize=10)
    # fig.savefig('bidding_tree.png')

    # print(prefix + 'bidding empty pricer: ')
    # print('\tcount: {}'.format(count_asks))
    # regression = DecisionTreeRegressor(max_depth=3)
    # x = np.array(bidding_x_empty, dtype=np.float32)
    # y = np.array(bidding_y_empty, dtype=np.float64)
    # x = x.reshape(-1, 1)
    # regression.fit(x, y)
    #
    # fig = plt.figure(figsize=(16, 10))
    # tree.plot_tree(regression, feature_names=['model util'], filled=True, fontsize=10)
    # fig.savefig('bidding_tree_empty.png')


if __name__ == '__main__':
    main()