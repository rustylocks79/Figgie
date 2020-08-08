import argparse
import pickle
import time

from game.agent.regret_agent import RegretAgent
from game.agent.basic_agent import BasicAgent, MinusOneAgent, PlusOneAgent
from game.model.history_model import HistoryModel
from game.model.simple_model import SimpleModel
from game.figgie import Figgie


def play(game: Figgie, agents: list, games: int, verbose=False):
    start_time = time.process_time()
    game.play(agents, games, verbose=verbose)
    total_time = time.process_time() - start_time
    print('Testing took {} seconds'.format(total_time))

    print('Results: ')
    for i, agent in enumerate(agents):
        print('agent {}: ({})'.format(i, type(agent)))
        print('\twins: {}'.format(agent.wins))
        print('\tavg. utility: {}, total utility: {}'.format(agent.total_utility / games, agent.total_utility))
        if isinstance(agent, RegretAgent):
            print('\tavg unknown states: {}, unknown states: {}'.format(agent.unknown_states / games, agent.unknown_states))

def load(file_name: str) -> dict:
    with open(file_name, 'rb') as file:
        strategy = pickle.load(file)
    return strategy

def main():
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-g', '--games', type=int, default=10_000, help='number of test games to run. ')
    parser.add_argument('-v', '--verbose', type=bool, default=False, help='output actions')
    args = parser.parse_args()

    game = Figgie()
    print('Parameters: ')
    print('\tgames: {}'.format(args.games))
    print()

    game_tree = load('strategies/strategy_100000_basic.pickle')
    agents = [MinusOneAgent(SimpleModel()),
              PlusOneAgent(SimpleModel()),
              PlusOneAgent(SimpleModel()),
              RegretAgent(SimpleModel(), game_tree=game_tree)]

    play(game, agents, args.games, args.verbose)


if __name__ == '__main__':
    main()
