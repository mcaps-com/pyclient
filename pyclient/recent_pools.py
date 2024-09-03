import pytz
from tzlocal import get_localzone
from api import make_get_request
from datetime import datetime

def query_recentpools():
    """Query the recent pools using the API."""
    return make_get_request("pump/recentpools")

def unix_to_local_datetime(unix_time):
    """Convert Unix time to a readable datetime format in the local timezone."""
    # Convert the Unix time to UTC datetime
    utc_dt = datetime.utcfromtimestamp(unix_time)
    
    # Get the local timezone of the system
    local_tz = get_localzone()
    
    # Convert the UTC datetime to local timezone
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    
    return local_dt.strftime('%Y-%m-%d %H:%M:%S')

# Example usage
if __name__ == "__main__":
    recentpools_data = query_recentpools()
    
    if recentpools_data:
        # Extract and print column names (header)
        columns = recentpools_data[0]
        print(columns)
        
        print(" | ".join(columns))
        
        # Print a separator line
        print("-" * 50)
        
        # Print each data row with unix_time_utc converted to local datetime
        for row in recentpools_data[1:]:
            # Convert the unix_time_utc column to local datetime
            unix_time_utc = row[columns.index("unix_time_utc")]
            datetime_local = unix_to_local_datetime(int(unix_time_utc))
            
            # Insert the formatted datetime at the start of the row
            row.insert(0, datetime_local)
            
            print(" | ".join(str(item) for item in row))
    else:
        print("No data found.")
