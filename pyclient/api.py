import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base API URL
BASE_URL = "http://mcaps.com/api/v0"

def get_jwt_token():
    """Load JWT token from environment variables."""
    return os.getenv("JWT_TOKEN")

def get_headers():
    """Return the headers required for the API request, including the Authorization token."""
    jwt_token = get_jwt_token()
    return {
        "Authorization": f"Bearer {jwt_token}"
    }

def make_get_request(endpoint):
    """Make a GET request to the specified endpoint with the required headers."""
    url = f"{BASE_URL}/{endpoint}"
    headers = get_headers()
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()
