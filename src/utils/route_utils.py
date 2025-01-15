"""Utility functions for flight route calculations."""

def calculate_flight_duration(origin: str, destination: str) -> float:
    """Calculate approximate flight duration in hours."""
    # Handle missing airports
    if not origin or not destination:
        return 2.0  # Default duration
        
    # Common Southwest Airlines routes with known durations
    ROUTE_DURATIONS = {
        ('KLAS', 'KLAX'): 1.0,  # Las Vegas to Los Angeles
        ('KLAX', 'KLAS'): 1.0,  # Los Angeles to Las Vegas
        ('KLAS', 'KPHX'): 1.2,  # Las Vegas to Phoenix
        ('KPHX', 'KLAS'): 1.2,  # Phoenix to Las Vegas
        ('KLAS', 'KSLC'): 1.5,  # Las Vegas to Salt Lake City
        ('KSLC', 'KLAS'): 1.5,  # Salt Lake City to Las Vegas
        ('KLAS', 'KDEN'): 2.0,  # Las Vegas to Denver
        ('KDEN', 'KLAS'): 2.0,  # Denver to Las Vegas
        ('KLAS', 'KSFO'): 1.5,  # Las Vegas to San Francisco
        ('KSFO', 'KLAS'): 1.5,  # San Francisco to Las Vegas
        ('KLAS', 'KOAK'): 1.5,  # Las Vegas to Oakland
        ('KOAK', 'KLAS'): 1.5,  # Oakland to Las Vegas
        ('KLAS', 'KSAN'): 1.0,  # Las Vegas to San Diego
        ('KSAN', 'KLAS'): 1.0,  # San Diego to Las Vegas
        ('KLAS', 'KBUR'): 1.0,  # Las Vegas to Burbank
        ('KBUR', 'KLAS'): 1.0,  # Burbank to Las Vegas
        ('KLAS', 'KONT'): 1.0,  # Las Vegas to Ontario
        ('KONT', 'KLAS'): 1.0,  # Ontario to Las Vegas
        ('KLAS', 'KSJC'): 1.5,  # Las Vegas to San Jose
        ('KSJC', 'KLAS'): 1.5,  # San Jose to Las Vegas
        ('KLAS', 'KSNA'): 1.0,  # Las Vegas to Santa Ana
        ('KSNA', 'KLAS'): 1.0,  # Santa Ana to Las Vegas
        ('KLAS', 'KTUS'): 1.2,  # Las Vegas to Tucson
        ('KTUS', 'KLAS'): 1.2,  # Tucson to Las Vegas
        ('KLAS', 'KRNO'): 1.2,  # Las Vegas to Reno
        ('KRNO', 'KLAS'): 1.2,  # Reno to Las Vegas
        ('KLAS', 'KSMF'): 1.5,  # Las Vegas to Sacramento
        ('KSMF', 'KLAS'): 1.5,  # Sacramento to Las Vegas
    }
    
    # Region-based durations (used when exact route not found)
    REGION_DURATIONS = {
        'West Coast': 1.5,      # CA, OR, WA
        'Southwest': 1.2,       # AZ, NM
        'Mountain': 2.0,        # CO, UT, MT, ID, WY
        'Midwest': 3.0,         # IL, MI, OH, IN, WI, MN
        'Texas': 2.5,           # TX, OK
        'Southeast': 4.0,       # FL, GA, NC, SC, TN
        'Northeast': 5.0,       # NY, MA, PA, NJ
    }
    
    # Try exact route first
    route = (origin, destination)
    if route in ROUTE_DURATIONS:
        return ROUTE_DURATIONS[route]
    
    # If not found, try region-based duration
    if origin.startswith('K') and destination.startswith('K'):
        # Extract state code from airport code (e.g., KLAS -> NV)
        origin_state = origin[1:3]
        dest_state = destination[1:3]
        
        # Map states to regions
        state_to_region = {
            'CA': 'West Coast', 'OR': 'West Coast', 'WA': 'West Coast',
            'AZ': 'Southwest', 'NM': 'Southwest',
            'CO': 'Mountain', 'UT': 'Mountain', 'MT': 'Mountain', 'ID': 'Mountain', 'WY': 'Mountain',
            'IL': 'Midwest', 'MI': 'Midwest', 'OH': 'Midwest', 'IN': 'Midwest', 'WI': 'Midwest', 'MN': 'Midwest',
            'TX': 'Texas', 'OK': 'Texas',
            'FL': 'Southeast', 'GA': 'Southeast', 'NC': 'Southeast', 'SC': 'Southeast', 'TN': 'Southeast',
            'NY': 'Northeast', 'MA': 'Northeast', 'PA': 'Northeast', 'NJ': 'Northeast'
        }
        
        # Get regions
        origin_region = state_to_region.get(origin_state)
        dest_region = state_to_region.get(dest_state)
        
        # If both regions found and different, use the longer duration
        if origin_region and dest_region and origin_region != dest_region:
            return max(REGION_DURATIONS[origin_region], REGION_DURATIONS[dest_region])
    
    # Default duration if no match found
    return 2.0 