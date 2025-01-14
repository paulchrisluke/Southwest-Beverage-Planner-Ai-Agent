# Excel File Conversion Guide

## Overview
I've provided a tool to convert Excel files containing beverage consumption data into the required CSV format for the AI prediction system. The converter is flexible and can handle various Excel formats commonly used for inventory tracking.

## Using the Converter

### Basic Usage
```bash
python src/data_processing/excel_converter.py input.xlsx
```

### Options
- `--sheet`: Specify which sheet to process (if multiple sheets exist)
- `--output`: Specify output CSV file path (default: input_converted.csv)

Example:
```bash
python src/data_processing/excel_converter.py inventory.xlsx --sheet "January 2024" --output jan_data.csv
```

## Excel File Format

### Required Information
Your Excel file should contain:
1. Flight information (number, date, time)
2. Route information (origin, destination)
3. Flight details (duration, passenger count)
4. Beverage consumption data

### Supported Column Names
The converter recognizes various common column names:

#### Flight Information
- Flight Number: `flight`, `flight number`, `flight_num`, `flight #`
- Date: `date`, `flight_date`, `departure_date`
- Time: `time`, `departure_time`, `departure`

#### Route Information
- Origin: `origin`, `from`, `departure airport`
- Destination: `destination`, `to`, `arrival airport`

#### Flight Details
- Duration: `duration`, `flight_duration`, `duration_hours`, `flight time`
- Passengers: `passengers`, `pax`, `passenger_count`, `capacity`

#### Beverage Names
The converter recognizes many common beverage names and variants:

##### Soft Drinks
- Coca-Cola/Coke
- Diet Coke
- Sprite
- Dr Pepper
- Diet Dr Pepper

##### Hot Beverages
- Coffee
- Decaf Coffee
- Hot Tea

##### Water & Juice
- Bottled Water
- Orange Juice
- Cranberry Apple Juice

##### Alcoholic Beverages
- Miller Lite
- Bud Light
- Wine (Red/White)
- Premium Spirits

### Sample Template
I've provided a sample Excel template (`sample_data_template.xlsx`) that shows the recommended format. You can:
1. Use it as a starting point
2. Copy your data into it
3. Modify it to match your existing format

### Notes
- The converter is case-insensitive
- Column names can be flexible (e.g., "Coca-Cola" or "Coke" or "coca cola")
- Empty cells are treated as zero consumption
- The converter will automatically:
  - Add "SWA" prefix to flight numbers if missing
  - Detect business/vacation routes
  - Calculate holiday dates
  - Validate passenger counts against aircraft types

### Common Issues and Solutions

1. **Missing Flight Numbers**
   - Ensure each row has a flight number
   - Numbers will automatically get "SWA" prefix if missing

2. **Date/Time Format**
   - Use standard Excel date format
   - Time can be in 24-hour (14:30) or 12-hour (2:30 PM) format

3. **Invalid Passenger Counts**
   - Should be either 143 (737-700) or 175 (737-800/MAX)
   - Other values will generate warnings

4. **Missing Beverage Data**
   - Empty cells are treated as zero
   - Negative values will be ignored

5. **Multiple Sheets**
   - Use --sheet option to specify which sheet to process
   - Process multiple sheets separately

### Example Conversion
Input Excel row:
```
Flight: 1234 | Date: 2/1/2024 | Time: 8:30 AM | From: BWI | To: MDW | Duration: 2.5 | Pax: 143 | Coke: 45 | Coffee: 30 | Water: 50 | Beer: 15
```

Output CSV rows:
```csv
SWA1234,1706745600,2.5,143,1,0,0,soft_drinks,45
SWA1234,1706745600,2.5,143,1,0,0,hot_beverages,30
SWA1234,1706745600,2.5,143,1,0,0,water_juice,50
SWA1234,1706745600,2.5,143,1,0,0,alcoholic,15
``` 