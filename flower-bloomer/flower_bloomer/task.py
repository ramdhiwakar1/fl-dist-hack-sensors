"""flower-bloomer: A Flower / PyTorch app."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from flwr_datasets import FederatedDataset
from flwr_datasets.partitioner import IidPartitioner
from flwr_datasets.partitioner import DirichletPartitioner
from torch.utils.data import DataLoader
from torchvision.transforms import Compose, Normalize, ToTensor


from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

# from datasets import load_dataset
# from flwr_datasets.partitioner import ChosenPartitioner


class Net(nn.Module):
    """Model (simple CNN adapted from 'PyTorch: A 60 Minute Blitz')"""

    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


fds = None  # Cache FederatedDataset

pytorch_transforms = Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])


def apply_transforms(batch):
    """Apply transforms to the partition from FederatedDataset."""
    batch["img"] = [pytorch_transforms(img) for img in batch["img"]]
    return batch


def load_data(partition_id: int, num_partitions: int):
    """Load partition sensors data."""
    # Only initialize `FederatedDataset` once
    global fds
    if fds is None:
        partitioner = IidPartitioner(num_partitions=num_partitions)
        fds = FederatedDataset(
            dataset="uoft-cs/cifar10",
            partitioners={"train": partitioner},
        )
    partition = fds.load_partition(partition_id)

    # Loading sensor data
    # Single file
    # data_files = r'fl-dist-hack-sensors\data\sensor.csv'
    # dataset = load_dataset("csv", data_files=data_files)

    # partitioner = DirichletPartitioner(num_partitions=num_partitions, partition_by="", alpha=1.0)
    # partitioner.dataset = dataset
    # partition = partitioner.load_partition(partition_id=0)

    # Divide data on each node: 80% train, 20% test
    partition_train_test = partition.train_test_split(test_size=0.2, seed=42)
    # Construct dataloaders
    partition_train_test = partition_train_test.with_transform(apply_transforms)
    trainloader = DataLoader(partition_train_test["train"], batch_size=32, shuffle=True)
    testloader = DataLoader(partition_train_test["test"], batch_size=32)
    return trainloader, testloader

def load_client_dataset(client_id: int):
    """Load one client's dataset from disk."""

    # Load the client's CSV
    df = pd.read_csv(f"federated_data/hybrid/client_{client_id}.csv")

    # Select sensor columns
    sensor_cols = [c for c in df.columns if c.startswith("sensor_")]

    X = df[sensor_cols].fillna(df[sensor_cols].mean()).values

    # Normalize
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # For CNN autoencoder, create sequences
    seq_len = 10
    seqs = [X[i:i+seq_len] for i in range(len(X)-seq_len)]
    seqs = np.array(seqs)

    # Train/test split
    X_train, X_test = train_test_split(seqs, test_size=0.2, shuffle=True)

    # Convert to PyTorch [batch, channels, length]
    X_train = torch.FloatTensor(X_train).permute(0, 2, 1)
    X_test = torch.FloatTensor(X_test).permute(0, 2, 1)

    train_loader = DataLoader(TensorDataset(X_train, X_train), batch_size=32, shuffle=True)
    val_loader = DataLoader(TensorDataset(X_test, X_test), batch_size=32, shuffle=False)

    return train_loader, val_loader

def train(net, trainloader, epochs, lr, device):
    """Train the model on the training set."""
    net.to(device)  # move model to GPU if available
    criterion = torch.nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.Adam(net.parameters(), lr=lr)
    net.train()
    running_loss = 0.0
    for _ in range(epochs):
        for batch in trainloader:
            images = batch["img"].to(device)
            labels = batch["label"].to(device)
            optimizer.zero_grad()
            loss = criterion(net(images), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
    avg_trainloss = running_loss / len(trainloader)
    return avg_trainloss


def test(net, testloader, device):
    """Validate the model on the test set."""
    net.to(device)
    criterion = torch.nn.CrossEntropyLoss()
    correct, loss = 0, 0.0
    with torch.no_grad():
        for batch in testloader:
            images = batch["img"].to(device)
            labels = batch["label"].to(device)
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
    accuracy = correct / len(testloader.dataset)
    loss = loss / len(testloader)
    return loss, accuracy
