import pybithumb
import numpy as np


crypto = "Enter the name of your cryptocurrency (ex: BTC, ETH, etc...)"


def get_ror(k = 0.5):
    df = pybithumb.get_ohlcv(crypto)

    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    commission = 0.0032

    df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] - commission, 1)

    return df['ror'].cumprod()[-2]


for k in np.arange(0.1, 1.0, 0.1):
    rate_of_return = get_ror(k)
    print("When k is", "%.1f" % k, ",", "rate of return is", "%f" % rate_of_return, "%")