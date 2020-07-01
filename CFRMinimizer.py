from random import uniform


class GameNode:
    def __init__(self, actions: list):
        self.actions = actions
        self.sumRegret = [0] * len(self.actions)
        self.sumStrategy = [0] * len(self.actions)

    def get_strategy(self) -> list:
        strategy = [0.0] * len(self.actions)
        sum = 0.0
        for i in range(len(self.actions)):
            if self.sumRegret[i] > 0:
                sum += self.sumRegret[i]

        for i in range(len(self.actions)):
            if sum > 0.0:
                strategy[i] = max(0.0, self.sumRegret[i] / sum)
            else:
                strategy[i] = 1.0 / len(self.actions)

        return strategy

    def __str__(self):
        result = ' '
        sum = 0
        for i in range(len(self.actions)):
            sum += self.sumStrategy[i]
        for i in range(len(self.actions)):
            result += '  '
            result += self.actions[i]
            result += ': '
            if sum == 0:
                result += str(1.0 / len(self.actions))
            else:
                result += str(self.sumStrategy[i] / sum)
        return result


class CFRMinimizer:
    def __init__(self, game):
        self.game = game
        self.game_tree = {}

    def train(self, trials: int):
        for i in range(trials):
            self.play_from(self.game, 1.0, 1.0, i % 2)
            self.game.reset()

    def play_from(self, game, pi: float, pi_prime: float, training_player: int) -> tuple:
        player = game.get_current_player()
        actions = game.get_actions()

        if game.is_finished():
            return game.get_utility(player) / pi_prime, 1.0

        info_set = game.get_current_info_set()
        if info_set in self.game_tree:
            node = self.game_tree[info_set]
        else:
            node = GameNode(actions)
            self.game_tree[info_set] = node

        strategy = node.get_strategy()

        probability = [0] * len(actions)
        epsilon = 0.6
        for action in range(len(actions)):
            if player == training_player:
                probability[action] = epsilon / len(actions) + (1.0 - epsilon) * strategy[action]
            else:
                probability[action] = strategy[action]

        selector = uniform(0, 1)
        choice = 0
        if selector > probability[0]:
            choice = 1

        game.preform('b' if choice == 0 else 'p')
        result = self.play_from(game, pi * strategy[choice], pi_prime * probability[choice],
                           training_player) if player == training_player else self.play_from(game, pi, pi_prime, training_player)

        util = -result[0]
        p_tail = result[1]

        if player == training_player:
            W = util * p_tail
            for action in range(len(actions)):
                regret = W * (1 - strategy[choice]) if action == choice else -W * strategy[choice]
                node.sumRegret[action] += regret
        else:
            for action in range(len(actions)):
                node.sumStrategy[action] += strategy[action] / pi_prime

        if player == training_player:
            return util, p_tail * strategy[choice]
        else:
            return util, p_tail

