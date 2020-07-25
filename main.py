import argparse
import pickle
import time
from random import randint

import numpy as np

from api.game import Game
from api.random_agent import RandomAgent
from api.strategy_agent import StrategyAgent
from games.figgie import Figgie, SUITS, ASK, BID, BUY, SELL, from_value


class BasicAgent(StrategyAgent):

    def generate_info_set(self, game: Game) -> str:
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

    def generate_actions(self, game: Game) -> np.ndarray:
        hand = game.cards[game.active_player]
        result = []
        for suit in SUITS:
            market = game.markets[suit.value]
            suit_code = suit.value * 10
            # asking
            if market.selling_price != 1 and hand[suit.value] >= 1:
                result.append(ASK * 100 + suit_code)

            # bidding
            if market.buying_price != 9:
                result.append((BID * 100) + suit_code)

            # buying
            if market.selling_price is not None and market.selling_player != game.get_active_player():
                result.append((BUY * 100) + suit_code)

            # selling
            if (market.buying_price is not None and market.buying_player != game.get_active_player()) and hand[
                suit.value] >= 1:
                result.append((SELL * 100) + suit_code)
        return np.array(result, dtype=int)

    def resolve_action(self, game: Game, initial_action: int) -> int:
        starting_action = initial_action
        op = initial_action // 100
        initial_action %= 100
        suit = from_value(initial_action // 10)
        if op == ASK:
            selling_price = game.markets[suit.value].selling_price
            return starting_action + randint(1, selling_price - 1 if selling_price is not None else 9)
        elif op == BID:
            buying_price = game.markets[suit.value].buying_price
            return starting_action + randint(buying_price + 1 if buying_price is not None else 1, 9)
        elif op == BUY or op == SELL:
            return starting_action
        else:
            raise ValueError('invalid initial action giving to mapping')


def save(strategy: dict, trials: int, info_set_method: str) -> str:
    file_name = 'strategies/strategy_{}_{}.pickle'.format(trials, info_set_method)
    with open(file_name, 'wb') as file:
        pickle.dump(strategy, file)
    return file_name


def load(file_name: str) -> dict:
    with open(file_name, 'rb') as file:
        strategy = pickle.load(file)
    return strategy


def play(game: Figgie, agents: list, games: int):
    game.reset()
    start_time = time.process_time()
    game.play(agents, games)
    total_time = time.process_time() - start_time
    print('\tTesting took {} seconds'.format(total_time))

    print('\tResults: ')
    for i, agent in enumerate(agents):
        print('\tagent {}'.format(i))
        print('\t\twins: {}'.format(agent.wins))
        print('\t\tavg. utility: {}, total utility: {}'.format(agent.total_utility / games, agent.total_utility))
        if isinstance(agent, StrategyAgent):
            print('\t\tavg unknown states: {}, unknown states: {}'.format(agent.unknown_states / games, agent.unknown_states))


def main():
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-t', '--trials', type=int, default=10_000, help='number of trials to run. ')
    parser.add_argument('-i', '--iterations', type=int, default=1, help='the number of times to train and run')
    parser.add_argument('-g', '--games', type=int, default=10_000, help='number of test games to run. ')
    args = parser.parse_args()

    game = Figgie()
    agent = BasicAgent()
    print('Parameters: ')
    print('\titerations: {}'.format(args.iterations))
    print('\ttrials: {}'.format(args.trials))
    print('\tgames: {}'.format(args.games))
    print()

    for i in range(1, args.iterations + 1):
        print('Iteration: {}'.format(i))

        start_time = time.process_time()
        agent.train(game, args.trials)
        total_time = time.process_time() - start_time
        print('\tTraining took {} seconds '.format(total_time))

        print('\tStrategy: ')
        print('\t\tinfo sets: {}'.format(len(agent.game_tree)))

        start_time = time.process_time()
        file_name = save(agent.game_tree, args.trials * i, 'basic')
        total_time = time.process_time() - start_time
        print('\tSaving to {} took {} seconds'.format(file_name, total_time))

        agents = [RandomAgent(),
                  RandomAgent(),
                  RandomAgent(),
                  agent]
        play(game, agents, args.games)

        print('---------------------------------------------------')


if __name__ == '__main__':
    main()
