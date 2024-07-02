import asyncio
import websockets
import requests
import time
#baseURL = 'http://www.mcaps.com/api/v0'
baseURL = 'http://mcaps.com/api/v0'

#https://pumpportal.fun/api/data/token-info?ca=Da34vU8FEqia19XGBNFHunpRy8yBZAxKqwQsEXd31WPg

def get_price(token):
    url = f"{baseURL}/price/pump/{token}"
    print(url)
    try:
        start_time = time.time()
        response = requests.get(url, headers={'Content-Type': 'application/json'})
        end_time = time.time()
        elapsed_time = end_time - start_time
        print('elapsed_time ', elapsed_time)
        response.raise_for_status()  # Raise an exception for HTTP errors
        responseData = response.json()
        #print(responseData['price_sol'])
        pd = round(responseData['price_usd'],9)
        print('usd price', pd)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error! Status: {http_err.response.status_code}")
    except Exception as err:
        print(f"Error: {err}")

def poll():
    # Example usage
    while True:
        #get_price('ApauDzZfW4HKKUZHqQGSF45uanz2wPUtA47XQ3eypump')
        #get_price('ApauDzZfW4HKKUZHqQGSF45uanz2wPUtA47XQ3eypump')
        get_price('4A4VVpAmwy2ngiosmpzogLuZEhCptzDCj5UrV9JTpump')
        time.sleep(3.0)


async def connect_to_server():
    uri = "ws://beta.mcaps.com/ws"
    print('connect ', uri)
    #uri = "ws://mcaps.com/pricefeed"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            while True:
                message = await websocket.recv()
                print(f"Received message: {message}")
    except Exception as e:
        print(f"Failed to connect or an error occurred: {e}")

def stream():
    asyncio.run(connect_to_server())

stream()
#poll()