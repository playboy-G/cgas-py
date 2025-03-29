import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(data)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("WebSocket closed")

def on_open(ws):
    ws.send(json.dumps({
        "op": "subscribe",
        "args": [{"channel": "tickers", "instId": "BTC-USDT"}]
    }))


