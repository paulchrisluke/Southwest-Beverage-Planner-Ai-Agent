#!/usr/bin/env python3
import os
import sys
import signal
import logging
import argparse
from datetime import datetime
import daemon
from daemon import pidfile
import lockfile

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.models.training_pipeline import TrainingPipeline

class TrainingService:
    """Service wrapper for the training pipeline."""
    
    def __init__(self):
        self.pipeline = None
        self.running = False
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

    def handle_signal(self, signum, frame):
        """Handle termination signals."""
        logging.info(f"Received signal {signum}")
        self.running = False

    def run(self):
        """Run the training service."""
        try:
            self.running = True
            self.pipeline = TrainingPipeline()
            
            logging.info("Starting training service")
            
            # Start scheduled training
            self.pipeline.schedule_training()
            
        except Exception as e:
            logging.error(f"Service failed: {str(e)}")
            sys.exit(1)

def setup_logging(log_dir: str):
    """Set up logging configuration."""
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(
        log_dir,
        f"training_service_{datetime.now().strftime('%Y%m%d')}.log"
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Training Pipeline Service')
    
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as a daemon service'
    )
    
    parser.add_argument(
        '--pid-file',
        default='/tmp/training_service.pid',
        help='PID file path (for daemon mode)'
    )
    
    parser.add_argument(
        '--log-dir',
        default='logs',
        help='Log directory path'
    )
    
    return parser.parse_args()

def run_service(args):
    """Run the service either in foreground or as daemon."""
    setup_logging(args.log_dir)
    
    if args.daemon:
        logging.info("Starting service in daemon mode")
        
        # Configure daemon context
        context = daemon.DaemonContext(
            working_directory=project_root,
            umask=0o002,
            pidfile=pidfile.TimeoutPIDLockFile(args.pid_file),
            detach_process=True
        )
        
        # Preserve file descriptors for logging
        context.files_preserve = [
            handler.stream.fileno() for handler in logging.getLogger().handlers
            if hasattr(handler, 'stream')
        ]
        
        try:
            # Start daemon
            with context:
                service = TrainingService()
                service.run()
        except lockfile.LockTimeout:
            logging.error("Service is already running")
            sys.exit(1)
            
    else:
        logging.info("Starting service in foreground")
        service = TrainingService()
        service.run()

def main():
    """Main entry point."""
    args = parse_args()
    
    try:
        run_service(args)
    except Exception as e:
        logging.error(f"Service failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 