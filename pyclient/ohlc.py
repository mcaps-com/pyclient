import pytz
from tzlocal import get_localzone
from api import make_get_request
from datetime import datetime

def query_ohlc():        
    return make_get_request("pump/ohlc/FZYZXyhfUhvGwpdkobJ9C725gB9yxig8x9BhQ9c5n6SU")

# Example usage
if __name__ == "__main__":
    data = query_ohlc()
    print(data)
    