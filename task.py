"""
Task: Pump Sensor Anomaly Detection using Convolutional Autoencoder
Lightweight implementation for demo purposes
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from pathlib import Path


# Simplified Autoencoder for faster training
class ConvAutoencoder(nn.Module):
    """Lightweight 1D Convolutional Autoencoder for sensor data"""
    
    def __init__(self, num_sensors=10, sequence_length=10):
        super(ConvAutoencoder, self).__init__()
        
        # Encoder (reduced complexity for demo)
        self.encoder = nn.Sequential(
            nn.Conv1d(num_sensors, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(16, num_sensors, kernel_size=2, stride=2),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded


def load_data(client_id: int, batch_size: int = 32):
    """
    Load and prepare sensor data for a specific client.
    Simplified for faster execution.
    """
    
    # Path to client data
    data_path = Path(f"federated_data/hybrid/client_{client_id}.csv")
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    # Load data
    df = pd.read_csv(data_path)
    
    # Use only first 10 sensors for faster training
    sensor_cols = [col for col in df.columns if col.startswith('sensor_')][:10]
    
    # Extract sensor data (use smaller subset for demo - 2000 samples)
    X = df[sensor_cols].fillna(df[sensor_cols].mean()).values[:2000]
    
    # Normalize to [0, 1]
    scaler = StandardScaler()
    X_normalized = scaler.fit_transform(X)
    X_normalized = (X_normalized - X_normalized.min()) / (X_normalized.max() - X_normalized.min() + 1e-8)
    
    # Create sequences
    sequence_length = 10
    sequences = []
    for i in range(len(X_normalized) - sequence_length + 1):
        sequences.append(X_normalized[i:i+sequence_length])
    
    sequences = np.array(sequences)
    
    # Split
    X_train, X_test = train_test_split(sequences, test_size=0.2, random_state=42)
    
    # Convert to tensors [batch, channels, seq_len]
    X_train_tensor = torch.FloatTensor(X_train).permute(0, 2, 1)
    X_test_tensor = torch.FloatTensor(X_test).permute(0, 2, 1)
    
    # Create DataLoaders
    train_dataset = TensorDataset(X_train_tensor, X_train_tensor)
    test_dataset = TensorDataset(X_test_tensor, X_test_tensor)
    
    trainloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    testloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    return trainloader, testloader, len(sensor_cols), sequence_length


def train(net, trainloader, epochs: int, learning_rate: float = 0.001):
    """Train the network (simplified for demo)"""
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=learning_rate)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net.to(device)
    
    net.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        for data, target in trainloader:
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = net(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        avg_loss = epoch_loss / len(trainloader)
        print(f"  Epoch {epoch+1}/{epochs}: Loss = {avg_loss:.4f}")
    
    return avg_loss


def test(net, testloader):
    """Evaluate the network"""
    criterion = nn.MSELoss()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net.to(device)
    
    net.eval()
    test_loss = 0.0
    with torch.no_grad():
        for data, target in testloader:
            data, target = data.to(device), target.to(device)
            output = net(data)
            loss = criterion(output, target)
            test_loss += loss.item()
    
    avg_loss = test_loss / len(testloader)
    return avg_loss, len(testloader.dataset)

