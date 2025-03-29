import pandas as pd

def calculate_ma(data, window):
    return data['close'].rolling(window=window).mean()

def simulate_strategy(data):
    data['ma_short'] = calculate_ma(data, 10)
    data['ma_long'] = calculate_ma(data, 30)
    data['signal'] = 0
    data['signal'][data['ma_short'] > data['ma_long']] = 1  # 买入信号
    data['signal'][data['ma_short'] < data['ma_long']] = -1 # 卖出信号
    return data

