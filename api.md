# Pump API Documentation

## Base URL
`/api/v0/pump`

### Endpoints

---

### 1. Get Recent Pools
**Endpoint:** `/recentpools`  
**Method:** `GET`  
**Description:** Retrieves a list of recent pools.  
**Response:**  
- `200 OK`: A list of recent pools.
- `500 Internal Server Error`: An error occurred while fetching the data.

---

### 2. Get Last Price
**Endpoint:** `/lastprice/{token}`  
**Method:** `GET`  
**Description:** Retrieves the last recorded price of the specified token.  
**Path Parameters:**  
- `token` (string): The token symbol or ID for which to retrieve the last price.  
**Response:**  
- `200 OK`: Returns the last price of the token.
- `404 Not Found`: Token not found.
- `500 Internal Server Error`: An error occurred while fetching the data.

---

### 3. Get OHLC Data
**Endpoint:** `/ohlc/{token}`  
**Method:** `GET`  
**Description:** Retrieves OHLC (Open, High, Low, Close) data for the specified token.  
**Path Parameters:**  
- `token` (string): The token symbol or ID for which to retrieve the OHLC data.  
**Response:**  
- `200 OK`: Returns the OHLC data.
- `404 Not Found`: Token not found.
- `500 Internal Server Error`: An error occurred while fetching the data.

---

### 4. Get Pool Information
**Endpoint:** `/poolinfo/{token}`  
**Method:** `GET`  
**Description:** Retrieves detailed information about the pool associated with the specified token.  
**Path Parameters:**  
- `token` (string): The token symbol or ID for which to retrieve the pool information.  
**Response:**  
- `200 OK`: Returns the pool information.
- `404 Not Found`: Token not found.
- `500 Internal Server Error`: An error occurred while fetching the data.

---

### 5. Get Price History
**Endpoint:** `/history/{token}`  
**Method:** `GET`  
**Description:** Retrieves historical price data for the specified token.  
**Path Parameters:**  
- `token` (string): The token symbol or ID for which to retrieve the historical price data.  
**Response:**  
- `200 OK`: Returns the historical price data.
- `404 Not Found`: Token not found.
- `500 Internal Server Error`: An error occurred while fetching the data.
