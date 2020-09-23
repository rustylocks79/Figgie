import os

from train import load


def main():
    for file in os.scandir('strategies/'):
        game_tree = load(file)
        print('{}: {}'.format(file, len(game_tree)))


if __name__ == '__main__':
    main()