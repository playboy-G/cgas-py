import requests
import time
import hmac
import hashlib

api_key = 'your_api_key'
secret_key = 'your_secret_key'
base_url = 'https://www.okx.com/api/v5'

# 获取账户信息
def get_balance():
    timestamp = str(int(time.time()))
    path = '/api/v5/account/balance'
    message = timestamp + 'GET' + path
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': 'your_passphrase'
    }

    response = requests.get(base_url + path, headers=headers)
    return response.json()