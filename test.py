import argparse
import time

from game.agent.one_action_agent import OneActionAgent
from game.agent.random_agent import RandomAgent
from game.agent.strategy_agent import StrategyAgent
from game.agent.basic_agent import BasicAgent
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
        if isinstance(agent, StrategyAgent):
            print('\tavg unknown states: {}, unknown states: {}'.format(agent.unknown_states / games, agent.unknown_states))


def main():
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-g', '--games', type=int, default=10_000, help='number of test games to run. ')
    parser.add_argument('-v', '--verbose', type=bool, default=False, help='output actions')
    args = parser.parse_args()

    game = Figgie()
    print('Parameters: ')
    print('\tgames: {}'.format(args.games))
    print()

    agents = [BasicAgent(0, SimpleModel()),
              BasicAgent(1, SimpleModel()),
              BasicAgent(2, SimpleModel()),
              BasicAgent(3, SimpleModel())]

    # agents = [RandomAgent(0),
    #           RandomAgent(1),
    #           RandomAgent(2),
    #           RandomAgent(3)]
    play(game, agents, args.games, args.verbose)


if __name__ == '__main__':
    main()
