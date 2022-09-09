import pybithumb
import time
import datetime
import requests
import schedule
from fbprophet import Prophet



crypto = "Enter the name of your cryptocurrency (ex: BTC, ETH, etc...)"
connect_key = "Enter your connect key"
secret_key =  "Enter your secret key"
my_token = "Enter your token"



def send_message(token, channel, text):
    """Send a message through Slack."""
    requests.post("https://slack.com/api/chat.postMessage", headers={"Authorization": "Bearer "+token}, data={"channel": channel,"text": text})



def get_target_price(ticker):
    """Get a target price of the cryptocurrency."""
    df = pybithumb.get_candlestick(ticker, chart_intervals = "24h")
    data_yesterday = df.iloc[-2]
    
    # lfy is low from yesterday.
    lfy = data_yesterday['low']

    # hfy is high from yesterday.
    hfy = data_yesterday['high']

    # oft is open from today.
    oft = data_yesterday['close']

    # 0.5 is the k value based on find_k.py.
    target_price = ((hfy - lfy) * 0.5) + oft
    return target_price



def get_mov_avg(ticker):
    """Calculate and get a moving average of the cryptocurrency."""
    df = pybithumb.get_candlestick(ticker)
    close = df['close']

    # mov_avg is moving average for 5 days.
    mov_avg = close.rolling(window=5).mean()
    return mov_avg[-2]



def buy_crypto(ticker):
    """Buy the cryptocurrency."""
    # tak is total amount of Korean won.
    tak = bithumb.get_balance(ticker)[2]
    orderbook = pybithumb.get_orderbook(ticker)
    sell_price = orderbook['asks'][0]['price']   
    value = tak/(float(sell_price))
    bithumb.buy_market_order(ticker, value)
    print(crypto + " has been bought for " + str(value))
    send_message(my_token,"#crypto", crypto + " has been bought for " + str(value))



def sell_crypto(ticker):
    """Sell the cryptocurrency."""
    value = bithumb.get_balance(ticker)[0]
    bithumb.sell_market_order(ticker, value)
    print(crypto + " has been sold for " + str(value))
    send_message(my_token,"#crypto", crypto + " has been sold for " + str(value))



# pcp is predicted close price.
pcp = 0

def predict_price(ticker):
    """Predict the close price of the cryptocurrency with Machine Learning, Prophet."""
    global pcp
    df = pybithumb.get_candlestick(crypto, chart_intervals="1h")
    df = df.tail(168)
    df = df.reset_index()

    # Get time (a) and close price (b)
    df['ds'] = df['time']
    df['y'] = df['close']
    data = df[['ds','y']]
    ai = Prophet()
    ai.fit(data)
    prediction = ai.make_future_dataframe(periods=24, freq='H')
    analysis = ai.predict(prediction)

    # Find close price before 00:00 a.m.
    close_price = analysis[analysis['ds'] == analysis.iloc[-1]['ds'].replace(hour=9)]

    # Find close price after 00:00 a.m.
    if len(close_price) == 0:
        close_price = analysis[analysis['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    vcp = close_price['yhat'].values[0]
    pcp = vcp

predict_price(crypto)
schedule.every().hour.do(lambda: predict_price(crypto))



# rn is the time right now.
rn = datetime.datetime.now()

# nd is the next day (00:00 a.m.).
nd = datetime.datetime(rn.year, rn.month, rn.day) + datetime.timedelta(1)
mov_avg = get_mov_avg(crypto)
target_price = get_target_price(crypto)



# Log into my Bithumb account.
bithumb = pybithumb.Bithumb(connect_key, secret_key)
print("Autotrade has been activated")
send_message(my_token,"#crypto", "Autotrade has been activated")



# Auto Trade
while True:
    try:
        rn = datetime.datetime.now()

        # 00:00 a.m. < right now < 11:59:50 p.m.
        if nd < rn < nd + datetime.timedelta(seconds = 10):
            target_price = get_target_price(crypto)
            nd = datetime.datetime(rn.year, rn.month, rn.day) + datetime.timedelta(1)
            mov_avg = get_mov_avg(crypto)
            sell_crypto(crypto)

        current_price = pybithumb.get_current_price(crypto)
        if (target_price < current_price) and (mov_avg < current_price) and (pcp < current_price):
            buy_crypto(crypto)

    except:
        print("An error occurred") 
        send_message(my_token,"#crypto", "An error occurred") 

    time.sleep(1)