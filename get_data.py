import pybithumb
import numpy as np


crypto = "Enter the name of your cryptocurrency (ex: BTC, ETH, etc...)"


# Candle stick represents one day's worth of price data about a cryptocurrency.
df = pybithumb.get_candlestick(crypto, chart_intervals = "24h")

# This chooses the last 2 months data.
df = df.tail(60)

# volatility range * k = (high - low) * k
df['range'] = (df['high'] - df['low']) * 0.5

# target is bid, shift down range column by 1
df['target'] = df['open'] + df['range'].shift(1)

commission = 0.0032

# ror is rate of return, np.where(if statement, when true, when false)
df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] - commission, 1)

# hpr is holding period return, hpr = cumulative product of rate of return
df['hpr'] = df['ror'].cumprod()

# dd = draw down, dd = ((cumulative maximum of hpr - current hpr) / cumulative maximum of hpr) * 100
df['dd'] = ((df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax()) * 100

# mdd is max draw down
print("MDD is", df['dd'].max(), "%")

# This prints the data in an Excel file.
df.to_excel("candle_chart.xlsx")