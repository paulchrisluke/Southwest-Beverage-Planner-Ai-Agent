# Data Format Documentation

## CSV File Format
The system expects CSV files containing beverage consumption data with specific columns and formats. A sample template is provided in `sample_data_template.csv`.

### Required Columns

1. `flight_number` (string)
   - Format: SWA followed by 4 digits (e.g., "SWA1234")
   - Must be a valid Southwest Airlines flight number

2. `timestamp` (integer)
   - Unix timestamp in seconds
   - Represents the flight departure time
   - Example: 1706745600 (February 1, 2024, 00:00:00 UTC)

3. `duration_hours` (float)
   - Flight duration in hours
   - Example: 2.5 for a 2.5-hour flight

4. `passenger_count` (integer)
   - Number of passengers on the flight
   - Should match aircraft capacity (typically 143 or 175 for Southwest)

5. `is_business_route` (integer)
   - 1 if the route is primarily business travel
   - 0 otherwise

6. `is_vacation_route` (integer)
   - 1 if the route involves vacation destinations
   - 0 otherwise

7. `is_holiday` (integer)
   - 1 if the flight is on a holiday
   - 0 otherwise

8. `beverage_type` (string)
   One of:
   - "soft_drinks"
   - "hot_beverages"
   - "water_juice"
   - "alcoholic"

9. `consumption_amount` (integer)
   - Number of beverages consumed
   - Should be a non-negative integer

### Example Row
```csv
SWA1234,1706745600,2.5,143,1,0,0,soft_drinks,120
```

### Notes
- Each flight should have entries for all beverage types
- Timestamps should be in UTC
- Boolean fields (is_business_route, is_vacation_route, is_holiday) must be 0 or 1
- The CSV should not contain headers
- Use comma (,) as the delimiter
- No quotes around strings unless they contain commas

### Common Issues
1. Invalid flight numbers (must start with SWA)
2. Incorrect timestamp format
3. Missing beverage types for flights
4. Invalid boolean values (use 0 or 1, not True/False)
5. Incorrect passenger counts for aircraft type 