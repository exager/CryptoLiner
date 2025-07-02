from flask import Flask, render_template
import json
import requests
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

@app.context_processor
def inject_year():
    return {'year': datetime.now().year}

@app.route("/")
def home():
    url = os.getenv('BACKEND_URL') + '/get-latest-data'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()  
        for k,v in data[0].items():
            if k=='recorded_time':
                last_update = v.split('T')
        last_update[1] = last_update[1].replace('-',':') + ' UTC'
        last_update = ' '.join(last_update)
        return render_template("index.html", coins = data, last_updated = last_update)
    else:
        return render_template("error.html", message = "Wrong EndPoint, Page Not Found::::")

# @app.route("/coin/<symbol>/details")
# def chart_page(symbol):
#     url = os.getenv('BACKEND_URL') + "/coin/" + symbol
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = pd.DataFrame(response.json())

#         # Getting the timestamp of the records
#         data['timestamp'] = pd.to_datetime(data['record_date'] + ' ' + data['record_time'])
#         data.sort_values('timestamp', inplace=True)

#         # And the moving averages
#         data['ma_7'] = data['price'].rolling(window=7).mean()
#         data['ma_24'] = data['price'].rolling(window=24).mean() 

#         chart_data = {
#             "timestamps": (data["record_date"] + " " + data["record_time"]).tolist(),
#             "price": data['price'].tolist(),
#             "ma_7": data['price'].rolling(7).mean().tolist(),
#             "ma_24": data['price'].rolling(24).mean().tolist()
#         }
#         return render_template("coin_dashboard.html", chart_data=chart_data)
#     else:
#         return render_template("error.html", message=f"Could not find details for {symbol} cryptocurrency"), 404

@app.route("/coin/<symbol>")
def coin_details(symbol):
    url = os.getenv('BACKEND_URL') + "/coin/" + symbol
    response = requests.get(url)
    if response.status_code == 200:
        
        df = pd.DataFrame(response.json())
        df = df.sort_values(by=["record_date", "record_time"])
        df['price'] = df['price'].astype(float)
        df["timestamps"] = df["record_date"] + " " + df["record_time"]
        timestamps = (df["record_date"] + " " + df["record_time"]).tolist()
        prices = df["price"].tolist()
        market_cap = df["market_cap"].tolist()
        volume = df["volume"].tolist() 
        price_change_24h = df["price_change_24h"].tolist() 
        price_change_percentage_24h = df["price_change_percentage_24h"].tolist()
        # And the moving averages
        ma_7= df['price'].rolling(window=7).mean().tolist() 
        ma_24 = df['price'].rolling(window=24).mean() .tolist() 
        coin_data = {
            "name": df["name"].iloc[-1],
            "rank": df["rank"].iloc[-1],
            "symbol": symbol,
            "timestamps": timestamps,
            "prices": prices,
            "ma_7": ma_7,
            "ma_24": ma_24,
            "market_cap": market_cap,
            "volume": volume,
            "price_change_24h": price_change_24h,
            "price_change_percentage_24h": price_change_percentage_24h,
            "last_updated": timestamps
        }
        url = "https://crypto-analyzer-service-1073952782451.us-central1.run.app/get-latest-data"
        response = requests.get(url)
        latest_data = {}
        if response.status_code == 200:
            data = response.json()
            for row in data:
                if row['symbol'] == symbol:
                    latest_data = row
                    break
        return render_template("coin_details.html", coin = coin_data, data = latest_data)
    else:
        return render_template("error.html", message=f"Could not find details for {symbol} cryptocurrency"), 404

@app.template_filter()
def comma_format(value):
    return "{:,}".format(value)

app.jinja_env.filters['comma_format'] = comma_format

