import yfinance as yf
import requests

# Test basic internet
response = requests.get("https://www.google.com")
print("Google:", response.status_code)

# Test Yahoo Finance directly
response = requests.get("https://finance.yahoo.com")
print("Yahoo Finance:", response.status_code)

# Try a simple stock fetch
stock = yf.Ticker("AAPL")
hist = stock.history(period="1d")
print(hist)