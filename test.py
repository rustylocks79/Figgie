import argparse

from api.random_agent import RandomAgent
from games.figgie import Figgie
from main import play, BasicAgent


def main():
    parser = argparse.ArgumentParser(description='Testing a strategy')
    parser.add_argument('-g', '--games', type=int, default=10_000, help='number of test games to run. ')
    args = parser.parse_args()
    agent = BasicAgent()
    agents = [RandomAgent(),
              RandomAgent(),
              RandomAgent(),
              agent]
    print('Testing Figgie')
    play(Figgie(), agents, args.games, verbose=False)


if __name__ == '__main__':
    main()
