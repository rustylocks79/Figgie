import argparse
import pickle

import numpy as np
import ray
import torch.optim
from ray import tune
from ray.tune.schedulers import ASHAScheduler
from torch.nn import Module, Linear, CrossEntropyLoss
from torch.nn.functional import relu, nll_loss, log_softmax
from torch.optim import Adam
from torch.utils.data import Dataset, DataLoader

INPUT_SIZE = 24
OUTPUT_SIZE = 4


class FiggieDataSet(Dataset):
    def __init__(self, samples) -> None:
        self.samples = samples

    def __getitem__(self, index: int):
        return self.samples[index]

    def __len__(self) -> int:
        return len(self.samples)


class Net(Module):
    def __init__(self, l1: int, l2: int, l3: int):
        super().__init__()
        self.fc1 = Linear(INPUT_SIZE, l1)
        self.fc2 = Linear(l1, l2)
        self.fc3 = Linear(l2, l3)
        self.fc4 = Linear(l3, OUTPUT_SIZE)

    def forward(self, x):
        x = relu(self.fc1(x))
        x = relu(self.fc2(x))
        x = relu(self.fc3(x))
        x = log_softmax(self.fc4(x), dim=1)
        return x


def train(model, optimizer, loss, train_loader):
    model.train()
    for batch_idx, (x, y) in enumerate(train_loader):
        model.zero_grad()
        output = model(x.view(-1, INPUT_SIZE))
        loss = nll_loss(output, y)
        loss.backward()
        optimizer.step()


def test(model, data_loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for batch_idx, (x, y) in enumerate(data_loader):
            output = model(x.view(-1, INPUT_SIZE))
            for idx, i in enumerate(output):
                if torch.argmax(i) == y[idx]:
                    correct += 1
                total += 1
    return correct / total


def train_figgie(config, checkpoint_dir=None):
    with open(r"/home/jmd6724/Documents/Figgie/ann/training_data.pickle", 'rb') as file:
        all_data = pickle.load(file)
    point = int(9 / 10 * len(all_data))
    train_data = FiggieDataSet(all_data[:point])
    test_data = FiggieDataSet(all_data[point:])
    train_set = DataLoader(train_data, batch_size=64, shuffle=True)
    test_set = DataLoader(test_data, batch_size=64, shuffle=False)

    model = Net(config['l1'], config['l2'], config['l3'])
    loss_function = CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=config['lr'])

    for epoch in range(10):
        train(model, optimizer, loss_function, train_set)
        acc = test(model, test_set)
        tune.report(mean_accuracty=acc)

        if epoch % 5 == 0:
            torch.save(model.state_dict(), r"/home/jmd6724/Documents/Figgie/ann/model_{}_{}_{}_{}.pth"
                       .format(config['l1'], config['l2'], config['l3'], acc))


def main():
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-in', '--input', type=str, help='the data')
    parser.add_argument('-out', '--output', type=str, help='where to store the model')
    args = parser.parse_args()

    config = {
        "l1": tune.sample_from(lambda _: 2 ** np.random.randint(2, 9)),
        "l2": tune.sample_from(lambda _: 2 ** np.random.randint(2, 9)),
        "l3": tune.sample_from(lambda _: 2 ** np.random.randint(2, 9)),
        "lr": tune.loguniform(1e-4, 1e-1),
    }
    ray.init(num_cpus=1, include_dashboard=False, local_mode=True)
    scheduler = ASHAScheduler(metric='mean_accuracy', mode='max')
    analysis = tune.run(train_figgie,
                        num_samples=4,
                        scheduler= scheduler,
                        config=config)

if __name__ == '__main__':
    main()
