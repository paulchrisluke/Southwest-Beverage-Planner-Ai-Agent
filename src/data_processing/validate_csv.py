import pandas as pd
import argparse
from datetime import datetime
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CSVValidator:
    REQUIRED_COLUMNS = [
        'flight_number',
        'timestamp',
        'duration_hours',
        'passenger_count',
        'is_business_route',
        'is_vacation_route',
        'is_holiday',
        'beverage_type',
        'consumption_amount'
    ]

    BEVERAGE_TYPES = [
        'soft_drinks',
        'hot_beverages',
        'water_juice',
        'alcoholic'
    ]

    AIRCRAFT_CAPACITIES = {
        'B737-700': 143,
        'B737-800': 175,
        'B737-MAX8': 175
    }

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.errors = []
        self.warnings = []

    def validate(self) -> bool:
        """Validate the CSV file and return True if valid."""
        try:
            df = pd.read_csv(self.filepath)
        except Exception as e:
            self.errors.append(f"Failed to read CSV file: {str(e)}")
            return False

        # Check columns
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            self.errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return False

        # Validate each row
        for idx, row in df.iterrows():
            self._validate_row(row, idx)

        # Check if all flights have all beverage types
        self._validate_beverage_coverage(df)

        # Report results
        if self.errors:
            logging.error("Validation failed with the following errors:")
            for error in self.errors:
                logging.error(f"- {error}")
        else:
            logging.info("CSV validation passed successfully!")

        if self.warnings:
            logging.warning("Warnings:")
            for warning in self.warnings:
                logging.warning(f"- {warning}")

        return len(self.errors) == 0

    def _validate_row(self, row, idx):
        """Validate a single row of data."""
        # Flight number format
        if not str(row['flight_number']).startswith('SWA'):
            self.errors.append(f"Row {idx}: Invalid flight number format: {row['flight_number']}")

        # Timestamp validation
        try:
            timestamp = int(row['timestamp'])
            dt = datetime.fromtimestamp(timestamp)
            if dt.year < 2024:
                self.warnings.append(f"Row {idx}: Timestamp is before 2024: {dt}")
        except:
            self.errors.append(f"Row {idx}: Invalid timestamp: {row['timestamp']}")

        # Duration validation
        if not (0 < float(row['duration_hours']) < 8):
            self.warnings.append(f"Row {idx}: Unusual flight duration: {row['duration_hours']} hours")

        # Passenger count validation
        if row['passenger_count'] not in [143, 175]:
            self.warnings.append(f"Row {idx}: Unusual passenger count: {row['passenger_count']}")

        # Boolean fields
        bool_fields = ['is_business_route', 'is_vacation_route', 'is_holiday']
        for field in bool_fields:
            if row[field] not in [0, 1]:
                self.errors.append(f"Row {idx}: Invalid {field} value: {row[field]}")

        # Beverage type validation
        if row['beverage_type'] not in self.BEVERAGE_TYPES:
            self.errors.append(f"Row {idx}: Invalid beverage type: {row['beverage_type']}")

        # Consumption amount validation
        if not (0 <= row['consumption_amount'] <= 500):
            self.warnings.append(f"Row {idx}: Unusual consumption amount: {row['consumption_amount']}")

    def _validate_beverage_coverage(self, df):
        """Check if all flights have entries for all beverage types."""
        flight_beverages = df.groupby('flight_number')['beverage_type'].unique()
        for flight, beverages in flight_beverages.items():
            missing = set(self.BEVERAGE_TYPES) - set(beverages)
            if missing:
                self.errors.append(f"Flight {flight} is missing beverage types: {', '.join(missing)}")

def main():
    parser = argparse.ArgumentParser(description='Validate Southwest Airlines beverage consumption CSV file')
    parser.add_argument('filepath', help='Path to the CSV file to validate')
    args = parser.parse_args()

    validator = CSVValidator(args.filepath)
    is_valid = validator.validate()

    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main() 