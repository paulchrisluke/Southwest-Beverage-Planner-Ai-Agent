import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
from typing import Optional, Tuple, List
import json
from sklearn.metrics import mean_squared_error, r2_score
import schedule
import time
import shutil

from src.models.retrain import ModelRetrainer
from src.data_processing.validate_csv import CSVValidator

class TrainingPipeline:
    """Manages the end-to-end model training pipeline."""
    
    def __init__(self, 
                config_path: str = 'config/training_config.json',
                model_dir: str = 'models',
                data_dir: str = 'data/training'):
        
        self.config_path = config_path
        self.model_dir = model_dir
        self.data_dir = data_dir
        
        # Create necessary directories
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Initialize logging
        self._setup_logging()
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize components
        self.retrainer = ModelRetrainer(model_dir)
        self.validator = CSVValidator()

    def _setup_logging(self):
        """Configure logging with rotation."""
        log_file = f"logs/training_pipeline_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def _load_config(self) -> dict:
        """Load training configuration."""
        default_config = {
            'validation_split': 0.2,
            'performance_threshold': 0.8,
            'min_training_samples': 1000,
            'max_training_files': 10,
            'training_schedule': {
                'frequency': 'daily',
                'time': '02:00'  # 2 AM
            },
            'backup': {
                'enabled': True,
                'keep_last': 5
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
        except Exception as e:
            logging.warning(f"Failed to load config: {str(e)}. Using defaults.")
        
        return default_config

    def run_pipeline(self) -> bool:
        """Execute the complete training pipeline."""
        try:
            logging.info("Starting training pipeline")
            
            # Step 1: Collect and validate training data
            training_files = self._collect_training_files()
            if not training_files:
                logging.warning("No valid training files found")
                return False
            
            # Step 2: Merge training data
            merged_data = self._merge_training_files(training_files)
            if merged_data.empty:
                logging.warning("No data after merging files")
                return False
            
            # Step 3: Validate merged dataset
            if not self._validate_merged_data(merged_data):
                logging.error("Merged data validation failed")
                return False
            
            # Step 4: Save temporary training file
            temp_training_file = os.path.join(
                self.data_dir,
                f"temp_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            merged_data.to_csv(temp_training_file, index=False)
            
            # Step 5: Retrain model
            success = self.retrainer.retrain(
                training_data_path=temp_training_file,
                validation_split=self.config['validation_split'],
                performance_threshold=self.config['performance_threshold']
            )
            
            # Cleanup
            os.remove(temp_training_file)
            
            if success:
                self._backup_successful_training(training_files)
                logging.info("Training pipeline completed successfully")
            else:
                logging.warning("Training pipeline completed with warnings")
            
            return success
            
        except Exception as e:
            logging.error(f"Training pipeline failed: {str(e)}")
            return False

    def _collect_training_files(self) -> List[str]:
        """Collect and validate training data files."""
        training_files = []
        
        # Get all CSV files in training directory
        for file in sorted(Path(self.data_dir).glob('*.csv')):
            if file.name.startswith('temp_') or file.name.startswith('.'):
                continue
                
            # Validate file
            if self.validator.validate(str(file)):
                training_files.append(str(file))
            else:
                logging.warning(f"Validation failed for {file}")
        
        # Limit number of files if needed
        if len(training_files) > self.config['max_training_files']:
            training_files = training_files[-self.config['max_training_files']:]
        
        return training_files

    def _merge_training_files(self, files: List[str]) -> pd.DataFrame:
        """Merge multiple training files into a single dataset."""
        dfs = []
        
        for file in files:
            try:
                df = pd.read_csv(file)
                dfs.append(df)
            except Exception as e:
                logging.error(f"Failed to read {file}: {str(e)}")
        
        if not dfs:
            return pd.DataFrame()
        
        merged_df = pd.concat(dfs, ignore_index=True)
        
        # Remove duplicates
        merged_df = merged_df.drop_duplicates()
        
        # Sort by timestamp
        if 'timestamp' in merged_df.columns:
            merged_df = merged_df.sort_values('timestamp')
        
        return merged_df

    def _validate_merged_data(self, data: pd.DataFrame) -> bool:
        """Validate the merged dataset."""
        if len(data) < self.config['min_training_samples']:
            logging.error(f"Insufficient training samples: {len(data)} < "
                        f"{self.config['min_training_samples']}")
            return False
        
        required_columns = [
            'flight_number', 'timestamp', 'duration_hours',
            'passenger_count', 'origin_airport', 'destination_airport',
            'soft_drinks', 'hot_beverages', 'water_juice', 'alcoholic'
        ]
        
        missing_cols = [col for col in required_columns if col not in data.columns]
        if missing_cols:
            logging.error(f"Missing required columns: {missing_cols}")
            return False
        
        # Check for invalid values
        if data['passenger_count'].min() < 0 or data['duration_hours'].min() < 0:
            logging.error("Found negative values in passenger_count or duration_hours")
            return False
        
        return True

    def _backup_successful_training(self, training_files: List[str]):
        """Backup training files after successful training."""
        if not self.config['backup']['enabled']:
            return
        
        backup_dir = os.path.join(self.data_dir, 'backup')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for file in training_files:
            try:
                filename = os.path.basename(file)
                backup_path = os.path.join(backup_dir, f"{timestamp}_{filename}")
                shutil.copy2(file, backup_path)
            except Exception as e:
                logging.error(f"Failed to backup {file}: {str(e)}")
        
        # Cleanup old backups
        self._cleanup_old_backups()

    def _cleanup_old_backups(self):
        """Remove old backup files."""
        backup_dir = os.path.join(self.data_dir, 'backup')
        if not os.path.exists(backup_dir):
            return
        
        backups = sorted(Path(backup_dir).glob('*.csv'))
        keep_last = self.config['backup']['keep_last']
        
        if len(backups) > keep_last:
            for backup in backups[:-keep_last]:
                try:
                    os.remove(backup)
                    logging.info(f"Removed old backup: {backup}")
                except Exception as e:
                    logging.error(f"Failed to remove backup {backup}: {str(e)}")

    def schedule_training(self):
        """Schedule periodic model retraining."""
        frequency = self.config['training_schedule']['frequency']
        time = self.config['training_schedule']['time']
        
        if frequency == 'daily':
            schedule.every().day.at(time).do(self.run_pipeline)
        elif frequency == 'weekly':
            schedule.every().monday.at(time).do(self.run_pipeline)
        elif frequency == 'monthly':
            schedule.every().day.at(time).do(self._check_monthly_schedule)
        
        logging.info(f"Scheduled training to run {frequency} at {time}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)

    def _check_monthly_schedule(self):
        """Check if it's time for monthly training."""
        if datetime.now().day == 1:  # Run on first day of month
            self.run_pipeline()

def main():
    """Run the training pipeline."""
    pipeline = TrainingPipeline()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--schedule':
        pipeline.schedule_training()
    else:
        pipeline.run_pipeline()

if __name__ == "__main__":
    main() 