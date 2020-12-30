import argparse

import matplotlib.pyplot as plt
import numpy as np
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor

from agent.info_sets.info_set_std import InfoSetStd
from agent.pricers.three_quarters_pricer import ThreeQuartersPricer
from figgie import Suit
from prog import load


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
    half_pricer = ThreeQuartersPricer()

    game_tree, trials = load(args.strategy)
    print('strategy at: {}'.format(args.strategy))
    print('\tnum info sets: {}'.format(len(game_tree)))
    print('\ttrials trained: {}'.format(trials))
    # print('\tmodels: {}'.format(model.name))
    print('\tinfo set generator: {}'.format(info_set.name))


    count_asks = 0
    count_asks_empty = 0

    asking_x = []
    asking_y = []

    for key in game_tree.keys():
        value = game_tree[key]
        strategy = value.get_trained_strategy()
        tokens = key.split(',')
        if tokens[0] == 'ask':
            card_util = int(tokens[1])
            selling_price = int(tokens[2]) if tokens[2] != 'N' else None
            actions = info_set.generate_ask_actions(card_util, selling_price, Suit.CLUBS)
            best_price = actions[strategy.argmax()]
            half_price = half_pricer.get_asking_price_internal(selling_price, card_util)
            if selling_price is not None:
                if best_price < 100:
                    count_asks += 1
                    asking_x.append([selling_price, card_util])
                    asking_y.append(best_price - half_price)
            else:
                count_asks_empty += 1
                # asking_x_empty.append(card_util)
                # asking_y_empty.append(best_price)

    print('\nResults\n')

    print('ask pricer: ')
    print('\tcount: {}'.format(count_asks))
    regression = DecisionTreeRegressor(max_depth=3)
    asking_x = np.array(asking_x, dtype=(np.float32, np.float32))
    asking_y = np.array(asking_y, dtype=np.float32)
    regression.fit(asking_x, asking_y)

    fig = plt.figure(figsize=(16, 10))
    tree.plot_tree(regression, feature_names=['market price', 'model util'], filled=True, fontsize=10)
    fig.savefig('asking_tree.png')


if __name__ == '__main__':
    main()