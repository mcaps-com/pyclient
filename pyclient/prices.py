import pytz
from tzlocal import get_localzone
from api import make_get_request
from datetime import datetime

def query_ohlc():        
    return make_get_request("pump/ohlc/FZYZXyhfUhvGwpdkobJ9C725gB9yxig8x9BhQ9c5n6SU")

def query_last(token):        
    return make_get_request(f"pump/lastprice/{token}")


if __name__ == "__main__":
    # data = query_ohlc()
    # print(data)
    token = "FZYZXyhfUhvGwpdkobJ9C725gB9yxig8x9BhQ9c5n6SU"
    data = query_last(token)
    print(data)
    