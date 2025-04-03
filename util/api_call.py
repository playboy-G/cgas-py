import base64
import hashlib
import hmac
import json
import time
from pipes import quote

import requests


class ApiCall:

    def __init__(self):
        self.host = 'https://fsscbip.chinagasholdings.com'
        self.app_name = '/iuap-api-gateway'
        self.app_key = 'af9b69ef564f48349f30fec248736778'
        self.app_secret = '510d020448d794457bd05d4650e54af5929bf418'
        self.endpoint = '/iuap-api-auth/open-auth/selfAppAuth/getAccessToken'


    def access_token(self):
        result_token = ''
        while True: # 时常会返回签名不正确，先用循环保证有数据
            timestamp = int(time.time() * 1000)
            content = 'appKey{}timestamp{}'.format(self.app_key, timestamp)
            digest = hmac.new(self.app_secret.encode('utf-8'), content.encode('utf-8'), digestmod=hashlib.sha256).digest()
            signature = quote(base64.b64encode(digest).decode('utf-8'))
            retry_times = 0
            response = requests.get(
                '{}{}?appKey={}&timestamp={}&signature={}'.format(self.host, self.endpoint, self.app_key, timestamp, signature))
            retry_times += 1
            body = json.loads(response.text)
            if body['code'] == '00000':
                result_token = body['data']['access_token']
                break
            elif retry_times > 5:
                break
        return result_token

    def http_post(self, url, payload):
        headers = {'Content-Type': 'application/json'}
        json_payload = ""
        if payload is not None:
            json_payload = json.dumps(payload)
        response = requests.post(url, data=json_payload, headers=headers)
        # print('接口: {}, 返回状态码: {}响应报文为: {}'.format(url, response.status_code, response.text))
        return response.text

    def http_post_headers(self, url, headers, payload):
        json_payload = ""
        if payload is not None:
            json_payload = json.dumps(payload)
        response = requests.post(url, data=json_payload, headers=headers)
        # print('接口: {}, 返回状态码: {}响应报文为: {}'.format(url, response.status_code, response.text))
        return response.text

    def call_api(self, url, payload):
        api_url = '{}{}{}?access_token={}&tenantId=npuaqm6k'.format(self.host, self.app_name, url, self.access_token())
        hits = self.http_post(api_url, payload)
        return hits

    def call_api_get(self, url, params):
        api_url = "{}{}{}?access_token={}&tenantId=npuaqm6k".format(self.host, self.app_name, url, self.access_token())
        response = requests.get(api_url, params=params)
        return response.text

    def call_api_with_token(self, url, token, payload):
        api_url = '{}{}{}?access_token={}&tenantId=npuaqm6k'.format(self.host, self.app_name, url, token)
        hits = self.http_post(api_url, payload)
        return hits

    def call_api_get_with_token(self, url, token, params):
        api_url = "{}{}{}?access_token={}&tenantId=npuaqm6k".format(self.host, self.app_name, url, token)
        response = requests.get(api_url, params=params)
        return response.text

    def call_api_delete(self, url, headers, data):
        response = requests.session().delete(url, headers=headers, data=data)
        return response.text

if __name__ == '__main__':
    api = ApiCall()
    print(api.access_token())

