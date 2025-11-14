"""
Flower ClientApp using modern API (Flower 1.23.0+)
Includes progress reporting for server monitoring
"""

from flwr.client import ClientApp, NumPyClient
from flwr.common import Context
import torch
from task import ConvAutoencoder, load_data, train, test
from collections import OrderedDict
import warnings
warnings.filterwarnings('ignore')


class FlowerClient(NumPyClient):
    """Flower client for federated learning with progress tracking"""
    
    def __init__(self, client_id: int, net, trainloader, testloader):
        self.client_id = client_id
        self.net = net
        self.trainloader = trainloader
        self.testloader = testloader
    
    def fit(self, parameters, config):
        """Train the model and report progress"""
        # Set model parameters
        self.set_parameters(parameters)
        
        # Get training config
        epochs = config.get("local_epochs", 2)  # Reduced for demo
        current_round = config.get("current_round", 0)
        
        print(f"\n{'='*60}")
        print(f"🏭 Client {self.client_id} | Round {current_round}")
        print(f"{'='*60}")
        print(f"📊 Training on {len(self.trainloader.dataset)} samples")
        print(f"🔄 Local epochs: {epochs}")
        
        # Train with progress reporting
        train_loss = train(self.net, self.trainloader, epochs=epochs)
        
        print(f"✅ Training complete! Loss: {train_loss:.4f}")
        
        # Return updated parameters and metrics with progress info
        return (
            self.get_parameters({}),
            len(self.trainloader.dataset),
            {
                "train_loss": float(train_loss),
                "client_id": self.client_id,
                "round": current_round,
                "status": "completed"
            }
        )
    
    def evaluate(self, parameters, config):
        """Evaluate the model"""
        self.set_parameters(parameters)
        
        current_round = config.get("current_round", 0)
        print(f"\n🔍 Client {self.client_id} | Evaluating (Round {current_round})...")
        
        test_loss, num_samples = test(self.net, self.testloader)
        
        print(f"📈 Test Loss: {test_loss:.4f}")
        
        return (
            float(test_loss),
            num_samples,
            {
                "test_loss": float(test_loss),
                "client_id": self.client_id,
                "round": current_round
            }
        )
    
    def get_parameters(self, config):
        """Extract model parameters"""
        return [val.cpu().numpy() for val in self.net.state_dict().values()]
    
    def set_parameters(self, parameters):
        """Load model parameters"""
        params_dict = zip(self.net.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.net.load_state_dict(state_dict, strict=True)


def client_fn(context: Context):
    """
    Factory function to create client instances.
    This is the modern Flower API pattern.
    """
    # Get client configuration from context
    partition_id = context.node_config["partition-id"]
    num_partitions = context.node_config.get("num-partitions", 3)
    
    print(f"\n🚀 Initializing Client {partition_id}/{num_partitions}")
    
    # Load data for this client
    trainloader, testloader, num_sensors, seq_length = load_data(
        client_id=partition_id,
        batch_size=32
    )
    
    # Create model
    net = ConvAutoencoder(num_sensors=num_sensors, sequence_length=seq_length)
    
    print(f"✅ Client {partition_id} ready with {len(trainloader.dataset)} training samples")
    
    # Return the client
    return FlowerClient(partition_id, net, trainloader, testloader).to_client()


# Create the ClientApp
app = ClientApp(client_fn=client_fn)


# Alternative: Direct execution (for non-deployment engine mode)
if __name__ == "__main__":
    import argparse
    from flwr.client import start_client
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", type=int, required=True, help="Client ID (0-4)")
    parser.add_argument("--server-address", type=str, default="127.0.0.1:8080",
                       help="Server address (default: 127.0.0.1:8080)")
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print(f"FEDERATED LEARNING CLIENT {args.client_id}")
    print(f"{'='*70}")
    print(f"Server: {args.server_address}")
    
    # Load data and create model
    trainloader, testloader, num_sensors, seq_length = load_data(args.client_id)
    net = ConvAutoencoder(num_sensors, seq_length)
    
    # Create and start client
    client = FlowerClient(args.client_id, net, trainloader, testloader)
    
    start_client(
        server_address=args.server_address,
        client=client.to_client()
    )

