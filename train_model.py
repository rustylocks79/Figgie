import argparse
import pickle

import torch.optim
from torch.nn import Module, Linear, CrossEntropyLoss
from torch.nn.functional import relu, nll_loss, log_softmax
from torch.optim import Adam
from torch.utils.data import Dataset, DataLoader

INPUT_SIZE = 24
OUTPUT_SIZE = 4


class Net(Module):
    def __init__(self):
        super().__init__()
        self.fc1 = Linear(INPUT_SIZE, 64)
        self.fc2 = Linear(64, 64)
        self.fc3 = Linear(64, 64)
        self.fc4 = Linear(64, OUTPUT_SIZE)

    def forward(self, x):
        x = relu(self.fc1(x))
        x = relu(self.fc2(x))
        x = relu(self.fc3(x))
        x = log_softmax(self.fc4(x), dim=1)
        return x


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a strategy using CFR')
    parser.add_argument('-in', '--input', type=str, help='the data')
    parser.add_argument('-out', '--output', type=str, help='where to store the model')
    args = parser.parse_args()
    with open(args.input, 'rb') as file:
        all_data = pickle.load(file)


    class FiggieDataSet(Dataset):
        def __init__(self, samples) -> None:
            self.samples = samples

        def __getitem__(self, index: int):
            return self.samples[index]

        def __len__(self) -> int:
            return len(self.samples)


    point = int(9/10 * len(all_data))
    train = FiggieDataSet(all_data[:point])
    test = FiggieDataSet(all_data[point:])
    train_set = DataLoader(train, batch_size=20, shuffle=True)
    test_set = DataLoader(test, batch_size=20, shuffle=False)

    net = Net()
    loss_function = CrossEntropyLoss()
    optimizer = Adam(net.parameters(), lr=0.001)

    for epoch in range(3):
        loss = 0
        for data in train_set:
            X, y = data
            net.zero_grad()
            output = net(X.view(-1, INPUT_SIZE))
            loss = nll_loss(output, y)
            loss.backward()
            optimizer.step()
        print(loss)

    correct = 0
    total = 0

    with torch.no_grad():
        for data in test_set:
            X, y = data
            output = net(X.view(-1, INPUT_SIZE))
            output = torch.exp(output)
            for idx, i in enumerate(output):
                if torch.argmax(i) == y[idx]:
                    correct += 1
                total += 1

    print("Accuracy: ", round(correct/total, 3))

    torch.save(net.state_dict(), args.output)
