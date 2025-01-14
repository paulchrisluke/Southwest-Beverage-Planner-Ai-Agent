import pandas as pd
import argparse
import logging
from datetime import datetime
import pytz
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ExcelConverter:
    """Converts Excel files to the required CSV format for the beverage prediction system."""
    
    BEVERAGE_MAPPINGS = {
        # Soft Drinks
        'coke': 'soft_drinks',
        'coca-cola': 'soft_drinks',
        'coca cola': 'soft_drinks',
        'diet coke': 'soft_drinks',
        'sprite': 'soft_drinks',
        'dr pepper': 'soft_drinks',
        'diet dr pepper': 'soft_drinks',
        'soda': 'soft_drinks',
        
        # Hot Beverages
        'coffee': 'hot_beverages',
        'regular coffee': 'hot_beverages',
        'decaf': 'hot_beverages',
        'decaf coffee': 'hot_beverages',
        'tea': 'hot_beverages',
        'hot tea': 'hot_beverages',
        
        # Water and Juice
        'water': 'water_juice',
        'bottled water': 'water_juice',
        'juice': 'water_juice',
        'orange juice': 'water_juice',
        'cranberry': 'water_juice',
        'apple juice': 'water_juice',
        'cranberry apple': 'water_juice',
        
        # Alcoholic
        'beer': 'alcoholic',
        'wine': 'alcoholic',
        'spirits': 'alcoholic',
        'liquor': 'alcoholic',
        'miller': 'alcoholic',
        'miller lite': 'alcoholic',
        'bud light': 'alcoholic',
        'white wine': 'alcoholic',
        'red wine': 'alcoholic'
    }
    
    VACATION_AIRPORTS = {
        'LAS', 'MCO', 'HNL', 'PHX',  # Las Vegas, Orlando, Honolulu, Phoenix
        'MIA', 'FLL', 'SAN', 'TPA'   # Miami, Ft Lauderdale, San Diego, Tampa
    }
    
    BUSINESS_ROUTES = {
        ('BWI', 'MDW'),  # Baltimore - Chicago
        ('DCA', 'ORD'),  # DC - Chicago
        ('LGA', 'ORD'),  # NYC - Chicago
        ('BOS', 'DCA')   # Boston - DC
    }

    def __init__(self):
        self.errors = []
        self.warnings = []

    def convert_excel(self, input_file: str, output_file: str, sheet_name: Optional[str] = None):
        """Convert Excel file to the required CSV format."""
        try:
            # Read Excel file
            df = pd.read_excel(input_file, sheet_name=sheet_name)
            logging.info(f"Successfully read Excel file: {input_file}")
            
            # Standardize column names
            df.columns = [col.lower().strip() for col in df.columns]
            
            # Process the data
            processed_data = []
            
            for idx, row in df.iterrows():
                try:
                    processed_rows = self._process_row(row)
                    processed_data.extend(processed_rows)
                except Exception as e:
                    self.errors.append(f"Error processing row {idx + 2}: {str(e)}")
            
            if not self.errors:
                # Create output DataFrame
                output_df = pd.DataFrame(processed_data)
                
                # Save to CSV
                output_df.to_csv(output_file, index=False)
                logging.info(f"Successfully converted and saved to: {output_file}")
                
                # Report any warnings
                for warning in self.warnings:
                    logging.warning(warning)
                    
                return True
            else:
                for error in self.errors:
                    logging.error(error)
                return False
                
        except Exception as e:
            logging.error(f"Failed to convert file: {str(e)}")
            return False

    def _process_row(self, row) -> List[Dict]:
        """Process a single row from the Excel file."""
        processed_rows = []
        
        # Extract flight information
        flight_num = self._extract_flight_number(row)
        timestamp = self._convert_to_timestamp(row)
        duration = self._extract_duration(row)
        passenger_count = self._extract_passenger_count(row)
        route_info = self._extract_route_info(row)
        
        # Process each beverage type
        beverages = self._extract_beverages(row)
        
        for bev_type, amount in beverages.items():
            processed_rows.append({
                'flight_number': flight_num,
                'timestamp': timestamp,
                'duration_hours': duration,
                'passenger_count': passenger_count,
                'is_business_route': int(route_info['is_business']),
                'is_vacation_route': int(route_info['is_vacation']),
                'is_holiday': int(self._is_holiday(timestamp)),
                'beverage_type': bev_type,
                'consumption_amount': amount
            })
        
        return processed_rows

    def _extract_flight_number(self, row) -> str:
        """Extract and validate flight number."""
        flight_num = None
        possible_columns = ['flight', 'flight_number', 'flight number', 'flight_num', 'flight num']
        
        for col in possible_columns:
            if col in row.index:
                flight_num = str(row[col]).strip().upper()
                break
        
        if not flight_num:
            raise ValueError("Flight number not found")
            
        if not flight_num.startswith('SWA'):
            flight_num = f"SWA{flight_num}"
        
        return flight_num

    def _convert_to_timestamp(self, row) -> int:
        """Convert date/time information to Unix timestamp."""
        date_cols = ['date', 'flight_date', 'departure_date']
        time_cols = ['time', 'departure_time', 'departure']
        
        # Find date column
        date_val = None
        for col in date_cols:
            if col in row.index and pd.notna(row[col]):
                date_val = row[col]
                break
        
        if not date_val:
            raise ValueError("Date information not found")
        
        # Find time column
        time_val = None
        for col in time_cols:
            if col in row.index and pd.notna(row[col]):
                time_val = row[col]
                break
        
        # Convert to datetime
        try:
            if isinstance(date_val, str):
                dt = pd.to_datetime(date_val)
            else:
                dt = pd.Timestamp(date_val)
            
            if time_val:
                if isinstance(time_val, str):
                    time_parts = time_val.split(':')
                    dt = dt.replace(hour=int(time_parts[0]), minute=int(time_parts[1]))
                elif isinstance(time_val, float):
                    hours = int(time_val)
                    minutes = int((time_val % 1) * 60)
                    dt = dt.replace(hour=hours, minute=minutes)
            
            return int(dt.timestamp())
        except Exception as e:
            raise ValueError(f"Invalid date/time format: {str(e)}")

    def _extract_duration(self, row) -> float:
        """Extract flight duration in hours."""
        duration_cols = ['duration', 'flight_duration', 'duration_hours', 'flight time']
        
        for col in duration_cols:
            if col in row.index and pd.notna(row[col]):
                try:
                    duration = float(row[col])
                    if 0 < duration < 24:  # Reasonable duration check
                        return duration
                except:
                    continue
        
        # If no duration found, estimate from departure and arrival times
        try:
            dep_time = self._convert_to_timestamp(row)
            arr_time = self._extract_arrival_time(row)
            if arr_time:
                return (arr_time - dep_time) / 3600
        except:
            pass
        
        self.warnings.append(f"Could not find duration for flight {row.get('flight_number', 'unknown')}")
        return 2.5  # Default average duration

    def _extract_passenger_count(self, row) -> int:
        """Extract passenger count."""
        pax_cols = ['passengers', 'pax', 'passenger_count', 'capacity']
        
        for col in pax_cols:
            if col in row.index and pd.notna(row[col]):
                try:
                    count = int(float(row[col]))
                    if count in [143, 175]:  # Known Southwest aircraft capacities
                        return count
                except:
                    continue
        
        self.warnings.append(f"Using default passenger count for flight {row.get('flight_number', 'unknown')}")
        return 143  # Default to 737-700 capacity

    def _extract_route_info(self, row) -> Dict:
        """Extract route information."""
        origin = None
        destination = None
        
        # Try to find origin/destination
        for col in row.index:
            col_lower = col.lower()
            if any(x in col_lower for x in ['origin', 'from', 'departure']):
                origin = str(row[col]).strip().upper()
            elif any(x in col_lower for x in ['destination', 'to', 'arrival']):
                destination = str(row[col]).strip().upper()
        
        is_business = False
        is_vacation = False
        
        if origin and destination:
            # Check if business route
            if (origin, destination) in self.BUSINESS_ROUTES or (destination, origin) in self.BUSINESS_ROUTES:
                is_business = True
            
            # Check if vacation route
            if origin in self.VACATION_AIRPORTS or destination in self.VACATION_AIRPORTS:
                is_vacation = True
        
        return {
            'is_business': is_business,
            'is_vacation': is_vacation
        }

    def _extract_beverages(self, row) -> Dict[str, int]:
        """Extract beverage consumption data."""
        beverages = {
            'soft_drinks': 0,
            'hot_beverages': 0,
            'water_juice': 0,
            'alcoholic': 0
        }
        
        # Look for beverage columns
        for col in row.index:
            col_lower = col.lower()
            
            # Skip non-beverage columns
            if any(x in col_lower for x in ['flight', 'date', 'time', 'route']):
                continue
            
            # Match column to beverage type
            for key, bev_type in self.BEVERAGE_MAPPINGS.items():
                if key in col_lower and pd.notna(row[col]):
                    try:
                        amount = int(float(row[col]))
                        if amount >= 0:
                            beverages[bev_type] += amount
                    except:
                        continue
        
        return beverages

    def _is_holiday(self, timestamp: int) -> bool:
        """Determine if the date is a holiday."""
        dt = datetime.fromtimestamp(timestamp)
        
        # Major US holidays (simplified)
        holidays = [
            (1, 1),    # New Year's Day
            (7, 4),    # Independence Day
            (12, 25),  # Christmas
            # Add more holidays as needed
        ]
        
        return (dt.month, dt.day) in holidays

def main():
    parser = argparse.ArgumentParser(description='Convert Excel files to Southwest Airlines beverage consumption CSV format')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--sheet', help='Sheet name to process (optional)')
    parser.add_argument('--output', help='Output CSV file path (optional)')
    
    args = parser.parse_args()
    
    # Generate output filename if not provided
    if not args.output:
        input_path = Path(args.input_file)
        args.output = str(input_path.parent / f"{input_path.stem}_converted.csv")
    
    converter = ExcelConverter()
    success = converter.convert_excel(args.input_file, args.output, args.sheet)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 