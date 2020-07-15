import pickle
import time

from figgie import Figgie
from games.game import StrategyAgent

if __name__ == '__main__':
    game = Figgie()

    print('Loading from file: ')
    start_time = time.process_time()
    with open('strategies/strategy.pickle', 'rb') as file:
        strategy = pickle.load(file)
    total_time = time.process_time() - start_time
    print('Loading from file took {} \n'.format(total_time))

    print('Found strategy with {} states \n'.format(len(strategy)))

    TOTAL_TRIALS = 10_000

    print('Playing {} games'.format(TOTAL_TRIALS))
    start_time = time.process_time()
    agents = [StrategyAgent(strategy),
              StrategyAgent(strategy),
              StrategyAgent(strategy),
              StrategyAgent(strategy)]
    game.reset()
    game.play(agents, TOTAL_TRIALS)
    total_time = time.process_time() - start_time
    print('Playing Took {}'.format(total_time))

    for i in range(len(agents)):
        print('agent {}'.format(i))
        print('\twins: {}'.format(agents[i].wins))
        print('\ttotal utility: {}'.format(agents[i].total_utility))
        print('\tavg. utility: {}'.format(agents[i].total_utility / TOTAL_TRIALS))
        if isinstance(agents[i], StrategyAgent):
            print('\tunknown states: {}'.format(agents[i].unknown_states))
            print('\tavg unknown states: {}'.format(agents[i].unknown_states / TOTAL_TRIALS))
