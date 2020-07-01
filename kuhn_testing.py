from math import sqrt

from CFRMinimizer import CFRMinimizer
from games.kuhn_poker import *

TOTAL_TRIALS = 10000

minimizer = CFRMinimizer(KuhnPoker())
minimizer.train(TOTAL_TRIALS)
node_map = minimizer.game_tree

alpha = 1.0 / 3 * node_map.get("0").sumStrategy[0] / (node_map.get("0").sumStrategy[0] + node_map.get("0").sumStrategy[1]) + 1.0 / 9 * node_map.get("2").sumStrategy[0] / (node_map.get("2").sumStrategy[0] + node_map.get("2").sumStrategy[1]) + 1.0 / 3 * (node_map.get("1pb").sumStrategy[0] / (node_map.get("1pb").sumStrategy[0] + node_map.get("1pb").sumStrategy[1]) - 1.0 / 3)

squareError = 0.0
keys = ["0", "0b", "0p", "0pb", "1", "1b", "1p", "1pb", "2", "2b", "2p", "2pb"]
targets = [alpha, 0.0, 1.0 / 3, 0.0, 0.0, 1.0 / 3, 0.0, alpha + 1.0 / 3, 3 * alpha, 1.0, 1.0, 1.0]
for i in range(len(keys)):
    node = node_map.get(keys[i])
    err = targets[i] - node.sumStrategy[0] / (node.sumStrategy[0] + node.sumStrategy[1])
    squareError += err * err


print("Results: RMSE over optimal strategy: {:.6f}".format(sqrt(squareError / TOTAL_TRIALS)))
print("Betting probabilities")
print("Key\tAveStrategy\tOptimal")
for i in range(len(keys)):
    node = node_map[keys[i]]
    print("{}\t{:.4f}\t{:.4f}".format(keys[i], node.sumStrategy[0] / (node.sumStrategy[0] + node.sumStrategy[1]), targets[i]))
