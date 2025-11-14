"""
Flower ServerApp using modern API (Flower 1.23.0+)
Includes progress tracking and metrics collection for dashboard
"""

from flwr.server import ServerApp, ServerConfig
from flwr.server.strategy import FedAvg
from flwr.common import Context, Metrics
from typing import List, Tuple, Optional, Dict
import json
from pathlib import Path
from datetime import datetime


class ProgressTrackingFedAvg(FedAvg):
    """
    FedAvg strategy with enhanced progress tracking and logging.
    Saves metrics for dashboard visualization.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics_history = []
        self.current_round = 0
        self.metrics_file = Path(__file__).parent.parent / "dashboard/training_metrics.json"
        self.metrics_file.parent.mkdir(exist_ok=True)
    
    def aggregate_fit(self, server_round, results, failures):
        """Aggregate training results with progress tracking"""
        self.current_round = server_round
        
        # Track client participation
        participating_clients = [metrics.get("client_id", "?") for _, metrics in results]
        
        print(f"\n{'='*70}")
        print(f"📊 ROUND {server_round} - AGGREGATION")
        print(f"{'='*70}")
        print(f"✅ Participating clients: {participating_clients}")
        print(f"❌ Failures: {len(failures)}")
        
        # Progress bar for aggregation
        if results:
            avg_train_loss = sum([metrics.get("train_loss", 0) for _, metrics in results]) / len(results)
            print(f"📈 Average Training Loss: {avg_train_loss:.4f}")
        
        # Call parent aggregation
        aggregated = super().aggregate_fit(server_round, results, failures)
        
        # Save metrics for dashboard
        self._save_metrics(server_round, results, "fit")
        
        print(f"✅ Aggregation complete!\n")
        
        return aggregated
    
    def aggregate_evaluate(self, server_round, results, failures):
        """Aggregate evaluation results with progress tracking"""
        
        print(f"\n{'='*70}")
        print(f"🔍 ROUND {server_round} - EVALUATION")
        print(f"{'='*70}")
        
        if results:
            # Calculate average test loss
            total_samples = sum([num_samples for _, num_samples, _ in results])
            weighted_losses = [
                loss * num_samples / total_samples
                for loss, num_samples, _ in results
            ]
            avg_test_loss = sum(weighted_losses)
            
            print(f"📊 Clients evaluated: {len(results)}")
            print(f"📈 Average Test Loss: {avg_test_loss:.4f}")
            
            # Progress visualization
            self._print_progress_bar(server_round, avg_test_loss)
            
            # Save evaluation metrics
            self._save_eval_metrics(server_round, results)
        
        return super().aggregate_evaluate(server_round, results, failures)
    
    def configure_fit(self, server_round, parameters, client_manager):
        """Configure training round with progress info"""
        config = {"local_epochs": 2, "current_round": server_round}
        
        print(f"\n{'='*70}")
        print(f"🚀 ROUND {server_round} - STARTING")
        print(f"{'='*70}")
        print(f"⚙️  Configuration: {config}")
        
        return super().configure_fit(server_round, parameters, client_manager)
    
    def configure_evaluate(self, server_round, parameters, client_manager):
        """Configure evaluation round"""
        config = {"current_round": server_round}
        return super().configure_evaluate(server_round, parameters, client_manager)
    
    def _print_progress_bar(self, current_round, loss, max_rounds=10):
        """Print ASCII progress bar"""
        progress = current_round / max_rounds
        bar_length = 40
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\n📊 Overall Progress:")
        print(f"[{bar}] {progress*100:.0f}% (Round {current_round}/{max_rounds})")
        print(f"Current Loss: {loss:.4f}")
    
    def _save_metrics(self, server_round, results, phase):
        """Save metrics to file for dashboard"""
        timestamp = datetime.now().isoformat()
        
        metrics_entry = {
            "timestamp": timestamp,
            "round": server_round,
            "phase": phase,
            "num_clients": len(results),
            "client_metrics": []
        }
        
        for _, metrics in results:
            metrics_entry["client_metrics"].append({
                "client_id": metrics.get("client_id", -1),
                "train_loss": metrics.get("train_loss", 0),
                "status": metrics.get("status", "unknown")
            })
        
        # Append to history
        self.metrics_history.append(metrics_entry)
        
        # Save to file
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
    
    def _save_eval_metrics(self, server_round, results):
        """Save evaluation metrics"""
        timestamp = datetime.now().isoformat()
        
        eval_entry = {
            "timestamp": timestamp,
            "round": server_round,
            "phase": "evaluate",
            "evaluations": []
        }
        
        for loss, num_samples, metrics in results:
            eval_entry["evaluations"].append({
                "client_id": metrics.get("client_id", -1),
                "test_loss": loss,
                "num_samples": num_samples
            })
        
        self.metrics_history.append(eval_entry)
        
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)


# Create strategy with progress tracking
strategy = ProgressTrackingFedAvg(
    fraction_fit=1.0,
    fraction_evaluate=1.0,
    min_fit_clients=2,
    min_evaluate_clients=2,
    min_available_clients=2,
)

# Create ServerApp
app = ServerApp(
    config=ServerConfig(num_rounds=5),  # Reduced for demo
    strategy=strategy,
)


# Alternative: Direct execution (for non-deployment engine mode)
if __name__ == "__main__":
    from flwr.server import start_server
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=5, help="Number of rounds")
    parser.add_argument("--min-clients", type=int, default=2, help="Min clients to start")
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print(f"🖥️  FEDERATED LEARNING SERVER")
    print(f"{'='*70}")
    print(f"Rounds: {args.rounds}")
    print(f"Min Clients: {args.min_clients}")
    print(f"Address: 0.0.0.0:8080")
    print(f"{'='*70}\n")
    
    strategy = ProgressTrackingFedAvg(
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=args.min_clients,
        min_evaluate_clients=args.min_clients,
        min_available_clients=args.min_clients,
    )
    
    start_server(
        server_address="0.0.0.0:8080",
        config=ServerConfig(num_rounds=args.rounds),
        strategy=strategy,
    )

