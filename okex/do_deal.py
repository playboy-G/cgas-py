import hashlib
import hmac
import json
import time
from turtle import pd

import requests
import websocket

from okex.balance import secret_key, api_key, base_url, get_balance
from okex.strategy import simulate_strategy
from okex.websocket_api import *


def place_order(side, symbol, quantity):
    timestamp = str(int(time.time()))
    path = '/api/v5/trade/order'
    message = timestamp + 'POST' + path + json.dumps({
        "instId": symbol,
        "tdMode": "cash",
        "side": side,
        "ordType": "market",
        "sz": str(quantity)
    })
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': 'your_passphrase'
    }

    response = requests.post(base_url + path, headers=headers, json={
        "instId": symbol,
        "tdMode": "cash",
        "side": side,
        "ordType": "market",
        "sz": str(quantity)
    })
    return response.json()

if __name__ == '__main__':

    # 获取账户信息
    print(get_balance())

    # 订阅实时 ticker 数据
    ws = websocket.WebSocketApp("wss://ws.okx.com:8443/ws/v5/public", on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

    # 示例数据
    data = pd.read_csv('market_data.csv')  # 假设你有历史市场数据
    strategy_data = simulate_strategy(data)
    print(strategy_data[['close', 'ma_short', 'ma_long', 'signal']].tail())

    # 根据策略信号下单
    if strategy_data['signal'].iloc[-1] == 1:
        place_order('buy', 'BTC-USDT', 0.001)
    elif strategy_data['signal'].iloc[-1] == -1:
        place_order('sell', 'BTC-USDT', 0.001)