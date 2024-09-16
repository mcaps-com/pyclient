import time
import pytz
from tzlocal import get_localzone
from api import make_get_request
from datetime import datetime


def query_ohlc(token):        
    return make_get_request(f"pump/ohlc/{token}")

def query_history(token):        
    return make_get_request(f"pump/history/{token}")

def query_last(token):        
    return make_get_request(f"pump/lastprice/{token}")

def query_info(token):    
    return make_get_request(f"pump/info/{token}")

def query_test():        
    result = make_get_request(f"test")
    print(result)
    result = make_get_request(f"test2")
    print(result)

if __name__ == "__main__":
    #query_test()
    token = "9WLGaJxYLAMHL6Ge3JrLnNrpEE4snDFU32gw6zpDpump"
    # data = query_last(token)
    # print(data)
    # time.sleep(1.5)

    # data = query_history(token)
    # print(data)
    # time.sleep(0.2)

    data = query_info(token)
    print(data)
    time.sleep(0.2)
    
    # print(data['price_sol'])
    # print(data['marketcap'])
    
    # # Get Unix time from data and convert to a datetime object in UTC
    # unix_time_utc = data['unix_time_utc']
    # utc_time = datetime.fromtimestamp(unix_time_utc, tz=pytz.utc)

    # # Get local timezone and current local time
    # local_tz = get_localzone() 
    # local_time = datetime.now(local_tz)

    # # Calculate the delta
    # delta = local_time - utc_time
    # print(f"Delta: {delta}")
