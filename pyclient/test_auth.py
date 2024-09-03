"""
testing auth
"""

import os
import requests
from dotenv import load_dotenv
load_dotenv()

# Replace with your actual token
jwt_token = os.getenv("JWT_TOKEN")

# Define the API endpoint
url = "http://mcaps.com/api/v0/test"

# Set the Authorization header with the Bearer token
headers = {
    "Authorization": f"Bearer {jwt_token}"
}

# Make the GET request to the server
response = requests.get(url, headers=headers)

# Print the response from the server
print(response.json())
