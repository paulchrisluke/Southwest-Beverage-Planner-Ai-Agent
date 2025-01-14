import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
from typing import Optional, Tuple
import joblib
from sklearn.metrics import mean_squared_error, r2_score

from src.models.predictor import BeveragePredictor

class ModelRetrainer:
    """Handles periodic retraining of the beverage prediction model."""
    
    def __init__(self, model_dir: str = 'models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{model_dir}/retraining.log"),
                logging.StreamHandler()
            ]
        )

    def retrain(self, 
                training_data_path: str,
                validation_split: float = 0.2,
                performance_threshold: float = 0.8) -> bool:
        """
        Retrain the model with new data and validate its performance.
        
        Args:
            training_data_path: Path to new training data
            validation_split: Fraction of data to use for validation
            performance_threshold: Minimum R² score required to accept new model
            
        Returns:
            bool: Whether the new model was accepted and saved
        """
        try:
            # Load and prepare data
            flight_data, consumption_data = self._load_training_data(training_data_path)
            
            # Split data
            train_flight, train_consumption, val_flight, val_consumption = \
                self._split_data(flight_data, consumption_data, validation_split)
            
            # Train new model
            new_model = BeveragePredictor()
            new_model.train(train_flight, train_consumption)
            
            # Evaluate new model
            val_predictions = new_model.predict(val_flight)
            new_performance = self._evaluate_model(val_consumption, val_predictions)
            
            # Compare with current model if exists
            current_model = self._load_current_model()
            if current_model:
                current_predictions = current_model.predict(val_flight)
                current_performance = self._evaluate_model(val_consumption, current_predictions)
                
                logging.info(f"Current model performance: {current_performance}")
                logging.info(f"New model performance: {new_performance}")
                
                if new_performance['r2'] <= current_performance['r2']:
                    logging.warning("New model does not improve performance. Keeping current model.")
                    return False
            
            # Check against threshold
            if new_performance['r2'] < performance_threshold:
                logging.warning(f"New model performance ({new_performance['r2']:.3f}) "
                              f"below threshold ({performance_threshold})")
                return False
            
            # Save new model
            self._save_model(new_model, new_performance)
            return True
            
        except Exception as e:
            logging.error(f"Retraining failed: {str(e)}")
            return False

    def _load_training_data(self, data_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and prepare training data."""
        try:
            data = pd.read_csv(data_path)
            
            # Split into features and targets
            feature_cols = [
                'flight_number', 'timestamp', 'duration_hours',
                'passenger_count', 'origin_airport', 'destination_airport'
            ]
            
            flight_data = data[feature_cols].copy()
            consumption_data = data[[
                'soft_drinks', 'hot_beverages',
                'water_juice', 'alcoholic'
            ]].copy()
            
            return flight_data, consumption_data
            
        except Exception as e:
            raise ValueError(f"Failed to load training data: {str(e)}")

    def _split_data(self,
                    flight_data: pd.DataFrame,
                    consumption_data: pd.DataFrame,
                    validation_split: float) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split data into training and validation sets."""
        # Sort by timestamp to avoid future data leakage
        sorted_indices = flight_data['timestamp'].argsort()
        flight_data = flight_data.iloc[sorted_indices]
        consumption_data = consumption_data.iloc[sorted_indices]
        
        # Split point
        split_idx = int(len(flight_data) * (1 - validation_split))
        
        return (
            flight_data.iloc[:split_idx],
            consumption_data.iloc[:split_idx],
            flight_data.iloc[split_idx:],
            consumption_data.iloc[split_idx:]
        )

    def _evaluate_model(self, 
                       actual: pd.DataFrame,
                       predicted: np.ndarray) -> dict:
        """Evaluate model performance."""
        mse = mean_squared_error(actual, predicted)
        rmse = np.sqrt(mse)
        r2 = r2_score(actual, predicted)
        
        # Calculate per-beverage metrics
        beverage_metrics = {}
        for i, bev_type in enumerate(['soft_drinks', 'hot_beverages', 'water_juice', 'alcoholic']):
            bev_mse = mean_squared_error(actual.iloc[:, i], predicted[:, i])
            bev_r2 = r2_score(actual.iloc[:, i], predicted[:, i])
            beverage_metrics[bev_type] = {
                'mse': bev_mse,
                'rmse': np.sqrt(bev_mse),
                'r2': bev_r2
            }
        
        return {
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'beverage_metrics': beverage_metrics,
            'timestamp': datetime.now().isoformat()
        }

    def _load_current_model(self) -> Optional[BeveragePredictor]:
        """Load the current production model if it exists."""
        model_path = os.path.join(self.model_dir, 'beverage_predictor.joblib')
        try:
            if os.path.exists(model_path):
                return BeveragePredictor.load_model(model_path)
        except Exception as e:
            logging.error(f"Failed to load current model: {str(e)}")
        return None

    def _save_model(self, model: BeveragePredictor, performance: dict):
        """Save the model and its performance metrics."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save model
        model_path = os.path.join(self.model_dir, 'beverage_predictor.joblib')
        model.save_model(model_path)
        
        # Save a backup
        backup_path = os.path.join(self.model_dir, f'beverage_predictor_{timestamp}.joblib')
        model.save_model(backup_path)
        
        # Save performance metrics
        metrics_path = os.path.join(self.model_dir, 'model_metrics.json')
        metrics = {
            'timestamp': timestamp,
            'performance': performance
        }
        pd.Series(metrics).to_json(metrics_path)
        
        logging.info(f"Saved new model with R² score: {performance['r2']:.3f}")
        
        # Keep only last 5 backup models
        self._cleanup_old_models()

    def _cleanup_old_models(self, keep_last: int = 5):
        """Remove old model backups, keeping only the N most recent."""
        backup_pattern = os.path.join(self.model_dir, 'beverage_predictor_*.joblib')
        backups = sorted(Path(self.model_dir).glob('beverage_predictor_*.joblib'))
        
        if len(backups) > keep_last:
            for backup in backups[:-keep_last]:
                try:
                    os.remove(backup)
                    logging.info(f"Removed old model backup: {backup}")
                except Exception as e:
                    logging.error(f"Failed to remove backup {backup}: {str(e)}")

def main():
    """Example usage of ModelRetrainer."""
    retrainer = ModelRetrainer()
    
    # Example: Retrain model with new data
    # success = retrainer.retrain(
    #     training_data_path='data/training/new_data.csv',
    #     validation_split=0.2,
    #     performance_threshold=0.8
    # )
    
    logging.info("Model retraining script completed")

if __name__ == "__main__":
    main() 