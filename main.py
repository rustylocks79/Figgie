from figgie import *
from bot.one_suit_player import *
from bot.simple_player import *

if __name__ == '__main__':
    fig = Figgie()
    player1 = SimplePlayer('player 1', fig, buy_tolerance=1, sell_tolerance=1)
    player2 = SimplePlayer('player 2', fig, buy_tolerance=1, sell_tolerance=1)
    player3 = SimplePlayer('player 3', fig, buy_tolerance=1, sell_tolerance=1)
    player4 = SimplePlayer('player 4', fig, buy_tolerance=1, sell_tolerance=1)

    fig.players.append(player1)
    fig.players.append(player2)
    fig.players.append(player3)
    fig.players.append(player4)

    wins = fig.play_games(num_games=1_000_000, rounds_per_game=5, verbose=False)
    for player in wins.keys():
        print('{} won {} games. '.format(player.name, wins[player]))
