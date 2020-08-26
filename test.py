import argparse
import pickle
import time

from game.agent.basic_agent import MinusOneAgent, PlusOneAgent
from game.agent.regret_agent import RegretAgent
from game.figgie import Figgie
from game.model.simple_model import SimpleModel


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
        print('\trmse of model: {}'.format(agent.get_rmse()))
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
    parser.add_argument('-s', '--strategy', type=str, default='strategies/strategy_10000_simple.pickle', help='the regret agent strategy')
    args = parser.parse_args()

    figgie = Figgie()
    print('Parameters: ')
    print('\tgames: {}'.format(args.games))
    print()

    game_tree = load(args.strategy)
    # agents = [MinusOneAgent(SimpleModel()),
    #           PlusOneAgent(SimpleModel()),
    #           PlusOneAgent(CheatingModel()),
    #           RegretAgent(SimpleModel(), PlusOneAgent(SimpleModel()), game_tree=game_tree)]

    agents = [MinusOneAgent(SimpleModel()),
              PlusOneAgent(SimpleModel()),
              MinusOneAgent(SimpleModel()),
              PlusOneAgent(SimpleModel())]

    play(figgie, agents, args.games, args.verbose)


if __name__ == '__main__':
    main()
